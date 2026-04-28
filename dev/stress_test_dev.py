# =============================================================================
# hdforce v2 - Stress Test against Dev API
# =============================================================================
#
# Real end-to-end test of every public API function against
# https://cloud.dev.hawkindynamics.com/api. Intended for pre-release validation;
# not included in the published wheel (this file lives under packages/hawkinPy/dev/,
# which Poetry does not include in the built distribution).
#
# SETUP (run these once, before executing this file):
#
#   # 1. Set the dev refresh token. This value never lives in the committed script.
#   export HAWKIN_KEY_DEV="<your dev refresh token>"    # bash/zsh
#   $env:HAWKIN_KEY_DEV = "<your dev refresh token>"    # PowerShell
#
# THEN, from the repo root:
#
#   poetry -C packages/hawkinPy run python packages/hawkinPy/dev/stress_test_dev.py
#
# OUTPUT:
#   - Pass/fail summary printed to console
#   - Detailed log written to packages/hawkinPy/dev/stress_test_dev_<timestamp>.log
#
# HOW DEV-API REDIRECTION WORKS:
#   hdforce's TokenManager falls back to https://cloud.dev.hawkindynamics.com/api
#   for any region value that is not "Americas", "Europe", or "Asia/Pacific".
#   This script passes region="Development" to trigger that fallback.
# =============================================================================

from __future__ import annotations

import csv
import datetime as dt
import os
import sys
import time
import traceback
from pathlib import Path

import pandas as pd

# Allow running this file directly from the repo root without `poetry run`
# by ensuring the package source dir is on sys.path.
_THIS_FILE = Path(__file__).resolve()
_PKG_ROOT = _THIS_FILE.parent.parent  # packages/hawkinPy
if str(_PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(_PKG_ROOT))

from hdforce import (  # noqa: E402
    AuthManager,
    CreateAthletes,
    GetAthletes,
    GetForceTime,
    GetForceTimeBulk,
    GetGroups,
    GetMetrics,
    GetTags,
    GetTeams,
    GetTests,
    GetTypes,
    LoggerConfig,
    UpdateAthletes,
)
from hdforce.Classes import Athlete, NewAthlete  # noqa: E402

LoggerConfig.Configure(level="info")


# --- Preflight checks --------------------------------------------------------

if not os.environ.get("HAWKIN_KEY_DEV"):
    raise SystemExit(
        "HAWKIN_KEY_DEV env var is not set. See the setup block at the top of "
        "this file for instructions."
    )


# --- Results table + helpers ------------------------------------------------

_stress_results: list[dict] = []


def _row_count(res) -> int | None:
    if isinstance(res, pd.DataFrame):
        return len(res)
    if isinstance(res, (list, tuple)):
        return len(res)
    if isinstance(res, dict):
        return len(res)
    return None


def run_step(name: str, fn, *args, **kwargs):
    """Run a step, time it, record pass/fail + row count, return the result."""
    print(f"\n=== {name} ===", flush=True)
    t0 = time.perf_counter()
    status = "PASS"
    rows: int | None = None
    msg = ""
    res = None
    try:
        res = fn(*args, **kwargs)
        rows = _row_count(res)
        print(f"  -> OK (rows={rows})", flush=True)
    except Exception as e:  # noqa: BLE001 - we intentionally catch anything
        status = "FAIL"
        msg = f"{type(e).__name__}: {e}"
        print(f"  -> FAIL: {msg}", flush=True)
        traceback.print_exc(limit=2)
    elapsed = round(time.perf_counter() - t0, 3)
    _stress_results.append({
        "step": name,
        "status": status,
        "rows": rows if rows is not None else "",
        "elapsed_s": elapsed,
        "message": msg,
    })
    return res


def expect_error_step(name: str, fn, *args, pattern: str | None = None, **kwargs):
    """Run a step that IS expected to raise. Pass if it does, fail if it doesn't."""
    print(f"\n=== {name} (expect error) ===", flush=True)
    t0 = time.perf_counter()
    status = "FAIL"
    msg = "No error was thrown, but one was expected."
    try:
        fn(*args, **kwargs)
    except Exception as e:  # noqa: BLE001
        caught = f"{type(e).__name__}: {e}"
        if pattern is None or pattern.lower() in caught.lower():
            status = "PASS"
            msg = f"Caught expected error: {caught}"
            print(f"  -> OK (caught: {caught})", flush=True)
        else:
            msg = f"Caught wrong error: {caught}"
            print(f"  -> FAIL: wrong error: {caught}", flush=True)
    elapsed = round(time.perf_counter() - t0, 3)
    _stress_results.append({
        "step": name,
        "status": status,
        "rows": "",
        "elapsed_s": elapsed,
        "message": msg,
    })


# --- Connect -----------------------------------------------------------------

run_step(
    "connect: AuthManager (manual method, region=Development fallback)",
    AuthManager,
    authMethod="manual",
    refreshToken=os.environ["HAWKIN_KEY_DEV"],
    region="Development",
)

if _stress_results and _stress_results[-1]["status"] == "FAIL":
    raise SystemExit("Could not authenticate. See connect step message.")


# --- Metadata endpoints ------------------------------------------------------

teams = run_step("metadata: GetTeams", GetTeams)
groups = run_step("metadata: GetGroups", GetGroups)
tags = run_step("metadata: GetTags", GetTags)
test_types = run_step("metadata: GetTypes", GetTypes)
metrics = run_step("metadata: GetMetrics", GetMetrics)
ath_active = run_step("metadata: GetAthletes (active only)", GetAthletes)
ath_all = run_step(
    "metadata: GetAthletes (includeInactive=True)",
    GetAthletes,
    includeInactive=True,
)


# --- Tests: core pagination --------------------------------------------------
#
# The Hawkin dev database spans years of trials; the API paginates at 1,000
# tests per page. Windows smaller than ~1 year often fit in a single page,
# so we escalate to cross the cursor threshold.

today = dt.date.today()
d_small = (today - dt.timedelta(days=30)).isoformat()
d_medium = (today - dt.timedelta(days=365)).isoformat()
d_large = (today - dt.timedelta(days=365 * 4)).isoformat()
d_epoch = "2015-01-01"

t_small = run_step(
    "tests: last 30 days (single-page sanity)",
    GetTests,
    from_=d_small,
)
t_medium = run_step(
    "tests: last 365 days",
    GetTests,
    from_=d_medium,
)
t_large = run_step(
    "tests: last 4 years (multi-page cursor)",
    GetTests,
    from_=d_large,
)
t_all = run_step(
    "tests: all-time since 2015 (max pagination stress)",
    GetTests,
    from_=d_epoch,
)


# --- Tests: filters (from/to applied) ---------------------------------------

filter_from = d_large
filter_to = today.isoformat()

if isinstance(ath_active, pd.DataFrame) and not ath_active.empty:
    sample_athlete_id = ath_active["id"].iloc[0]
    run_step(
        "tests: filter by athleteId (single, 4 years)",
        GetTests,
        from_=filter_from,
        to_=filter_to,
        athleteId=sample_athlete_id,
    )

if isinstance(teams, pd.DataFrame) and not teams.empty:
    run_step(
        "tests: filter by teamId (single, 4 years)",
        GetTests,
        from_=filter_from,
        to_=filter_to,
        teamId=teams["id"].iloc[0],
    )
    if len(teams) >= 2:
        multi_team_ids = teams["id"].head(10).tolist()
        run_step(
            f"tests: filter by teamId (multi, n={len(multi_team_ids)}, 4 years)",
            GetTests,
            from_=filter_from,
            to_=filter_to,
            teamId=multi_team_ids,
        )

if isinstance(groups, pd.DataFrame) and not groups.empty:
    run_step(
        "tests: filter by groupId (single, 4 years)",
        GetTests,
        from_=filter_from,
        to_=filter_to,
        groupId=groups["id"].iloc[0],
    )

if isinstance(test_types, pd.DataFrame) and not test_types.empty:
    # GetTypes returns a 'canonicalId' column; GetTests accepts canonical ID.
    type_col = "canonicalId" if "canonicalId" in test_types.columns else test_types.columns[0]
    run_step(
        "tests: filter by typeId (single, 4 years)",
        GetTests,
        from_=filter_from,
        to_=filter_to,
        typeId=test_types[type_col].iloc[0],
    )


# --- Tests: sync mode --------------------------------------------------------
#
# syncFrom 1 year ago exercises cursor pagination in sync mode on large orgs.

sync_from_epoch = int(dt.datetime.combine(
    today - dt.timedelta(days=365), dt.time.min,
).timestamp())
run_step(
    "tests: sync mode (syncFrom 1 year ago, multi-page)",
    GetTests,
    sync=True,
    from_=sync_from_epoch,
)


# --- Tests: includeInactive toggle ------------------------------------------

run_step(
    "tests: includeInactive=True (1 year)",
    GetTests,
    from_=d_medium,
    includeInactive=True,
)


# --- Forcetime ---------------------------------------------------------------

sample_test_id: str | None = None
for cand in (t_small, t_medium, t_large, t_all):
    if isinstance(cand, pd.DataFrame) and not cand.empty and "id" in cand.columns:
        sample_test_id = str(cand["id"].iloc[0])
        break

if sample_test_id:
    run_step(
        f"forcetime: single (id={sample_test_id})",
        GetForceTime,
        testId=sample_test_id,
    )

if isinstance(t_small, pd.DataFrame) and not t_small.empty and "id" in t_small.columns:
    bulk_ids = t_small["id"].head(10).tolist()
    run_step(
        f"forcetime: bulk (n={len(bulk_ids)})",
        GetForceTimeBulk,
        test_ids=bulk_ids,
    )


# --- Token refresh forced ----------------------------------------------------

def _force_refresh_and_call():
    # Expire the access token by rewriting the env var the package reads on
    # every request via ensure_token(). The next API call must re-auth.
    os.environ["TOKEN_EXPIRATION"] = "0"
    return GetTeams()


run_step("token-refresh: force expiry and re-call", _force_refresh_and_call)


# --- Error paths -------------------------------------------------------------

expect_error_step(
    "error: GetForceTime with bogus ID",
    GetForceTime,
    testId="does-not-exist-xxxxxxxxxxxxxxxxxxxxxxxxx",
)

expect_error_step(
    "error: GetTests with invalid 'from_' value",
    GetTests,
    from_="not-a-date",
    pattern="date",
)

expect_error_step(
    "error: GetTests with two entity filters (validation)",
    GetTests,
    from_=d_small,
    athleteId="any",
    teamId="any",
    pattern="only one of",
)


# --- Bulk athletes (safe, clearly-labeled test records) ---------------------

stress_name = f"STRESSTEST_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}"
created_id: str | None = None


def _create_stress_athlete():
    global created_id
    results = CreateAthletes(athletes=[NewAthlete(name=stress_name, active=True)])
    if results and results[0].successful:
        created_id = results[0].id
    return results


run_step(
    f"athletes: CreateAthletes ({stress_name})",
    _create_stress_athlete,
)

if created_id:
    run_step(
        f"athletes: UpdateAthletes ({stress_name} -> active=False)",
        UpdateAthletes,
        athletes=[Athlete(id=created_id, name=stress_name, active=False)],
    )


# --- Summary -----------------------------------------------------------------

print("\n\n================== STRESS TEST SUMMARY ==================")
for r in _stress_results:
    print(
        f"  {r['status']:4s}  {r['elapsed_s']:>7.3f}s  "
        f"rows={str(r['rows']):>8s}  {r['step']}"
    )
    if r["message"]:
        print(f"        {r['message']}")
print("---------------------------------------------------------")
n_pass = sum(1 for r in _stress_results if r["status"] == "PASS")
n_fail = sum(1 for r in _stress_results if r["status"] == "FAIL")
total_time = sum(r["elapsed_s"] for r in _stress_results)
print(
    f"Result: {n_pass} / {len(_stress_results)} PASS ({n_fail} FAIL). "
    f"Total time: {total_time:.1f}s."
)
print("=========================================================\n")


# --- Write full log ---------------------------------------------------------

log_dir = _THIS_FILE.parent
log_path = log_dir / f"stress_test_dev_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
try:
    with open(log_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["step", "status", "rows", "elapsed_s", "message"]
        )
        writer.writeheader()
        writer.writerows(_stress_results)
    print(f"Detailed log written to: {log_path}")
except OSError as e:
    print(f"Could not write log to {log_path}: {e}")

if n_fail > 0:
    sys.exit(1)
