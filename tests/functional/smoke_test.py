#!/usr/bin/env python3
# =============================================================================
# hdforce (hawkinPy) — End-to-End Smoke Test
# =============================================================================
#
# PURPOSE
#   Exercise every public function in hdforce once, in the order a real user
#   would call them, against a live Hawkin Dynamics API. This is a *smoke test*
#   (one representative call per scenario, pass/fail recorded) — a fast
#   confidence check that the package is wired up correctly end to end.
#
#   It covers: auth + token lifecycle, offline metadata, org metadata, test
#   queries (every filter), force-time (single + bulk + export), the optional
#   write path (create/update athletes), and expected error paths.
#
# -----------------------------------------------------------------------------
# HOW TO RUN
# -----------------------------------------------------------------------------
#   From the repo root (with hdforce importable — installed, or run from
#   packages/hawkinPy so the local `hdforce/` package is on sys.path):
#
#       cd packages/hawkinPy
#       python smoke_test.py
#
#   Edit the CONFIG block below first (token + settings).
#
# -----------------------------------------------------------------------------
# SUPPLYING THE TOKEN  (mirrors AuthManager's three auth methods)
# -----------------------------------------------------------------------------
#   HD_AUTH_METHOD = "manual"  (default, recommended for a smoke test):
#       The token is used to authenticate but is NOT written to disk or the
#       system environment. Paste it into HD_TOKEN below. The access token
#       lives only in os.environ['ACCESS_TOKEN'] for this process.
#
#   HD_AUTH_METHOD = "env":
#       The token is read from (or written to) the HD_REFRESH_TOKEN_NAME system
#       environment variable. Paste a token into HD_TOKEN to set it for this
#       session, or leave HD_TOKEN = "" if the env var is already exported.
#
#   HD_AUTH_METHOD = "file":
#       The token is read from / written to a .env file (HD_ENV_FILE). Paste a
#       token into HD_TOKEN to write it, or leave "" if the file already has it.
#
# -----------------------------------------------------------------------------
# SECURITY NOTE
# -----------------------------------------------------------------------------
#   Prefer "manual" or an already-exported env var over committing a token.
#   This file should never be committed with a real token in HD_TOKEN.
# =============================================================================

import os
import re
import sys
import csv
import time
import datetime
import importlib.util


# =============================================================================
# 1. CONFIG  —  EDIT THIS BLOCK
# =============================================================================

# --- Token ---------------------------------------------------------------
# Paste your refresh / integration token here, OR leave "" and supply it via
# the system environment ("env") or a .env file ("file") ahead of time.
HD_TOKEN = ""

# --- Auth + connection settings ------------------------------------------
HD_AUTH_METHOD        = "env"                # "manual" | "env" | "file"  (env = read HD_REFRESH_TOKEN; CI uses this)
HD_REGION             = "Americas"           # "Americas","Europe","Asia/Pacific","Development"
HD_REFRESH_TOKEN_NAME = "HD_REFRESH_TOKEN"   # env-var / .env key name (env & file methods)
HD_ENV_FILE           = ".env"               # path to .env file (file method only)
HD_ORG_NAME           = None                 # org endpoint; None -> "v1" (standard users)

# --- Logging -------------------------------------------------------------
# When HD_LOG_TO_FILE is True, the package's internal logs (at HD_LOG_LEVEL) go
# to HD_LOG_FILE; this harness still prints its own PASS/FAIL lines to the
# console regardless, so you get both a watchable console and a debug log file.
HD_LOG_LEVEL   = "debug"          # "debug","info","warning","error","critical"
HD_LOG_TO_FILE = True
HD_LOG_FILE    = "smoke_test_hdforce_{ts}.log".format(
    ts=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
)

# --- Date windows for test queries (YYYY-MM-DD; dtConverter handles these) ---
_today         = datetime.date.today()
HD_FROM_RECENT = (_today - datetime.timedelta(days=30)).isoformat()    # ~last month
HD_FROM_WIDE   = (_today - datetime.timedelta(days=365)).isoformat()   # ~last year
HD_TO          = _today.isoformat()                                    # today

# --- Safety switches -----------------------------------------------------
# Write operations CREATE a real athlete in your org (and then deactivate it).
# Leave False for a read-only smoke test. Set True only when you accept that a
# clearly-labelled SMOKETEST_* athlete will be created in the target org.
RUN_WRITE_TESTS = False

# Limit how many force-time trials the bulk steps pull, to keep things quick.
HD_BULK_LIMIT = 5


# =============================================================================
# 2. IMPORT THE PACKAGE
# =============================================================================
# Allow running directly from packages/hawkinPy without installing.
_here = os.path.dirname(os.path.abspath(__file__))
if os.path.isdir(os.path.join(_here, "hdforce")) and _here not in sys.path:
    sys.path.insert(0, _here)

try:
    import pandas as pd
    from hdforce import (
        AuthManager, LoggerConfig,
        GetTypes, GetMetrics,
        GetAthletes, GetTeams, GetGroups, GetTags,
        GetTests, GetForceTime, GetForceTimeBulk, GetCOP,
        CreateAthletes, UpdateAthletes,
    )
    # NewAthlete / Athlete are NOT re-exported from the top-level package in
    # the current __init__.py, so import them from their module directly.
    from hdforce.Classes import NewAthlete, Athlete  # noqa: F401
except Exception as exc:  # pragma: no cover - import guard
    print("FATAL: could not import hdforce. Make sure it is installed or run "
          "this script from packages/hawkinPy.\n  ->", exc)
    sys.exit(1)


# =============================================================================
# 3. TEST HARNESS
# =============================================================================
# Each step runs a zero-argument callable so the harness controls timing and
# catches exceptions uniformly. Results accumulate in a list of dicts.

_RESULTS = []  # list of {step, status, rows, elapsed_s, detail}


def _count(x):
    """Best-effort size of a result for at-a-glance sanity checking."""
    if x is None:
        return None
    if isinstance(x, pd.DataFrame):
        return len(x)
    if isinstance(x, (list, tuple)):
        return len(x)
    return None


def _record(step, status, rows, elapsed, detail):
    _RESULTS.append({
        "step": step, "status": status, "rows": rows,
        "elapsed_s": elapsed, "detail": detail,
    })


def _last_passed():
    return bool(_RESULTS) and _RESULTS[-1]["status"] == "PASS"


def step(name, fn):
    """Standard step: ANY exception => FAIL. Returns the call's value (or None)."""
    print(f"\n--- {name}")
    t0 = time.perf_counter()
    try:
        res = fn()
        elapsed = round(time.perf_counter() - t0, 3)
        rows = _count(res)
        print(f"    PASS  (n = {rows}, {elapsed}s)")
        _record(name, "PASS", rows, elapsed, "")
        return res
    except Exception as e:
        elapsed = round(time.perf_counter() - t0, 3)
        detail = f"{type(e).__name__}: {e}"
        print(f"    FAIL  {detail}")
        _record(name, "FAIL", None, elapsed, detail)
        return None


def step_expect_error(name, fn, pattern=None):
    """Inverted step: an exception is the EXPECTED outcome.

    Optionally require the exception text to match `pattern` (regex).
    """
    print(f"\n--- {name}  (expect error)")
    t0 = time.perf_counter()
    try:
        fn()
        elapsed = round(time.perf_counter() - t0, 3)
        print("    FAIL  no error was raised, but one was expected")
        _record(name, "FAIL", None, elapsed, "no error raised")
    except Exception as e:
        elapsed = round(time.perf_counter() - t0, 3)
        msg = f"{type(e).__name__}: {e}"
        if pattern is None or re.search(pattern, str(e), re.IGNORECASE):
            print(f"    PASS  (caught: {msg})")
            _record(name, "PASS", None, elapsed, f"caught: {msg}")
        else:
            print(f"    FAIL  wrong error: {msg}")
            _record(name, "FAIL", None, elapsed, f"wrong error: {msg}")


def step_skip(name, reason):
    """Explicitly skipped step (records why, so the summary is honest)."""
    print(f"\n--- {name}\n    SKIP  {reason}")
    _record(name, "SKIP", None, None, reason)



def main():
    # =============================================================================
    # 4. PRE-FLIGHT
    # =============================================================================

    print("\n=========================================================")
    print("  hdforce smoke test")
    print(f"  method={HD_AUTH_METHOD}  region={HD_REGION}  org={HD_ORG_NAME or 'v1'}")
    print(f"  write-tests={RUN_WRITE_TESTS}  bulk-limit={HD_BULK_LIMIT}")
    print("=========================================================")

    # Configure logging. file=True sends package logs to a file at HD_LOG_LEVEL;
    # this harness prints its own progress via plain print() either way.
    # NOTE: the implemented method is LoggerConfig.Configure (the docs' name
    # "LoggerConfig.Configuration" is incorrect for the shipped code).
    LoggerConfig.Configure(level=HD_LOG_LEVEL, file=HD_LOG_TO_FILE, file_path=HD_LOG_FILE)
    if HD_LOG_TO_FILE:
        print(f"[setup] package logs -> {HD_LOG_FILE} (level={HD_LOG_LEVEL})")


    # =============================================================================
    # 5. AUTHENTICATE
    # =============================================================================
    # AuthManager performs the refresh-token -> access-token handshake and stashes
    # ACCESS_TOKEN / TOKEN_EXPIRATION / CLOUD_URL where the data functions can find
    # them. Token shape differs by method (see header).

    def _connect():
        token = HD_TOKEN if HD_TOKEN else None

        if HD_AUTH_METHOD == "manual":
            if token is None:
                raise ValueError("manual auth requires a token in HD_TOKEN.")
            AuthManager(authMethod="manual", region=HD_REGION,
                        refreshToken=token, orgName=HD_ORG_NAME)

        elif HD_AUTH_METHOD == "env":
            # token=None -> read existing HD_REFRESH_TOKEN_NAME env var.
            # token set  -> store it under that name for this session.
            AuthManager(authMethod="env", region=HD_REGION,
                        refreshToken_name=HD_REFRESH_TOKEN_NAME,
                        refreshToken=token, orgName=HD_ORG_NAME)

        elif HD_AUTH_METHOD == "file":
            AuthManager(authMethod="file", region=HD_REGION,
                        refreshToken_name=HD_REFRESH_TOKEN_NAME,
                        refreshToken=token, env_file_name=HD_ENV_FILE,
                        orgName=HD_ORG_NAME)
        else:
            raise ValueError(f"Unknown HD_AUTH_METHOD: {HD_AUTH_METHOD!r}")

        # Confirm the access token landed where the data functions look for it.
        if not os.getenv("ACCESS_TOKEN"):
            raise RuntimeError("ACCESS_TOKEN not set after AuthManager().")
        return os.getenv("CLOUD_URL")

    step("connect: AuthManager handshake", _connect)
    CONNECTED = _last_passed()
    if CONNECTED:
        print(f"    cloud URL = {os.getenv('CLOUD_URL')}")
    else:
        print("\n[!] Could not authenticate — network steps will be skipped.")
        print("    Check the token, region, auth method, and org name.")


    # =============================================================================
    # 6. OFFLINE METADATA  (no token — should pass even without a connection)
    # =============================================================================
    # GetTypes is a static table; GetMetrics reads the bundled MetricDictionary
    # parquet (requires a parquet engine such as pyarrow).

    step("offline: GetTypes()", lambda: GetTypes())

    step("offline: GetMetrics() — all", lambda: GetMetrics())
    # NOTE: GetMetrics() does NOT raise on an unknown test_type — it silently
    # returns the full dictionary. So this is a normal call, not an error path.
    step("offline: GetMetrics('CMJ')", lambda: GetMetrics("CMJ"))
    step("offline: GetMetrics('Isometric Test')", lambda: GetMetrics("Isometric Test"))


    # =============================================================================
    # 7. ORG METADATA  (network)
    # =============================================================================

    teams = groups = ath_active = ath_all = None
    if CONNECTED:
        teams      = step("org: GetTeams()",  lambda: GetTeams())
        groups     = step("org: GetGroups()", lambda: GetGroups())
        step("org: GetTags()", lambda: GetTags())
        ath_active = step("org: GetAthletes() — active only",
                          lambda: GetAthletes())
        ath_all    = step("org: GetAthletes(includeInactive=True)",
                          lambda: GetAthletes(includeInactive=True))

        def _check_inactive():
            assert isinstance(ath_active, pd.DataFrame)
            assert isinstance(ath_all, pd.DataFrame)
            if len(ath_all) < len(ath_active):
                raise AssertionError(
                    f"all={len(ath_all)} < active={len(ath_active)} (unexpected)")
            return True
        step("org: includeInactive returns >= active-only", _check_inactive)
    else:
        step_skip("org: metadata endpoints", "no connection")


    # =============================================================================
    # 8. TEST QUERIES  (network)  —  every filter path
    # =============================================================================

    tests_recent = None
    if CONNECTED:

        # --- Date windows -------------------------------------------------------
        tests_recent = step("tests: from recent window",
                            lambda: GetTests(from_=HD_FROM_RECENT))
        step("tests: from/to bounded window",
             lambda: GetTests(from_=HD_FROM_RECENT, to_=HD_TO))

        # --- Filter by test type (canonical id, then abbreviation) --------------
        cmj_id = None
        _types = GetTypes()
        if isinstance(_types, pd.DataFrame) and "Countermovement Jump" in set(_types["name"]):
            cmj_id = _types.loc[_types["name"] == "Countermovement Jump", "canonicalId"].iloc[0]
        if cmj_id:
            step("tests: filter by typeId (canonical CMJ id)",
                 lambda: GetTests(from_=HD_FROM_WIDE, to_=HD_TO, typeId=cmj_id))
        step("tests: filter by typeId (abbreviation 'CMJ')",
             lambda: GetTests(from_=HD_FROM_WIDE, to_=HD_TO, typeId="CMJ"))

        # --- Filter by athlete --------------------------------------------------
        if isinstance(ath_active, pd.DataFrame) and len(ath_active) > 0:
            _aid = ath_active["id"].iloc[0]
            step("tests: filter by athleteId (single)",
                 lambda: GetTests(from_=HD_FROM_WIDE, to_=HD_TO, athleteId=_aid))
        else:
            step_skip("tests: filter by athleteId", "no athletes in roster")

        # --- Filter by team (single + multi up to 10) ---------------------------
        if isinstance(teams, pd.DataFrame) and len(teams) > 0:
            step("tests: filter by teamId (single)",
                 lambda: GetTests(from_=HD_FROM_WIDE, to_=HD_TO, teamId=teams["id"].iloc[0]))
            if len(teams) >= 2:
                _team_ids = teams["id"].head(10).tolist()
                step("tests: filter by teamId (multi, list)",
                     lambda: GetTests(from_=HD_FROM_WIDE, to_=HD_TO, teamId=_team_ids))
        else:
            step_skip("tests: filter by teamId", "no teams in org")

        # --- Filter by group ----------------------------------------------------
        if isinstance(groups, pd.DataFrame) and len(groups) > 0:
            step("tests: filter by groupId (single)",
                 lambda: GetTests(from_=HD_FROM_WIDE, to_=HD_TO, groupId=groups["id"].iloc[0]))
        else:
            step_skip("tests: filter by groupId", "no groups in org")

        # --- Sync mode (pulls by modified/uploaded time, not test time) ---------
        step("tests: sync mode (syncFrom recent)",
             lambda: GetTests(from_=HD_FROM_WIDE, sync=True))

        # --- includeInactive (server-side toggle, API v1.13+) -------------------
        step("tests: includeInactive=True",
             lambda: GetTests(from_=HD_FROM_RECENT, includeInactive=True))

        # --- includeEid (equipment id column) -----------------------------------
        step("tests: includeEid=True",
             lambda: GetTests(from_=HD_FROM_RECENT, includeEid=True))

        # --- Inspect DataFrame envelope attrs -----------------------------------
        def _check_attrs():
            df = GetTests(from_=HD_FROM_RECENT)
            for key in ("Count", "Last Sync", "Last Test Time"):
                if key not in df.attrs:
                    raise AssertionError(f"missing DataFrame attr: {key!r}")
            print(f"    attrs -> Count={df.attrs['Count']}  "
                  f"LastSync={df.attrs['Last Sync']}  "
                  f"LastTestTime={df.attrs['Last Test Time']}")
            return df
        step("tests: DataFrame carries Count / Last Sync / Last Test Time attrs",
             _check_attrs)

    else:
        step_skip("tests: all query scenarios", "no connection")


    # =============================================================================
    # 9. FORCE-TIME  (network)  —  single, bulk, and export
    # =============================================================================

    if CONNECTED:

        # Choose a representative test id. Prefer the recent window; fall back to a
        # wider pull if the recent window came back empty.
        ids_source = None
        sample_test_id = None
        if isinstance(tests_recent, pd.DataFrame) and len(tests_recent) > 0 \
                and "id" in tests_recent.columns:
            ids_source = tests_recent
        else:
            _wide = GetTests(from_=HD_FROM_WIDE, to_=HD_TO)
            if isinstance(_wide, pd.DataFrame) and len(_wide) > 0 and "id" in _wide.columns:
                ids_source = _wide
        if ids_source is not None:
            sample_test_id = ids_source["id"].iloc[0]

        if sample_test_id is not None:

            # --- Single force-time trial ---------------------------------------
            def _single():
                df = GetForceTime(testId=sample_test_id)
                print(f"    athlete={df.attrs.get('Athlete Name')}  "
                      f"type={df.attrs.get('Test Name')}  samples={len(df)}")
                return df
            step(f"forcetime: single trial ({sample_test_id})", _single)

            # --- Bulk from an explicit list of ids (in-memory) -----------------
            _bulk_ids = ids_source["id"].head(HD_BULK_LIMIT).tolist()
            step(f"forcetime: bulk from id list (n={len(_bulk_ids)}, in-memory)",
                 lambda: GetForceTimeBulk(test_ids=_bulk_ids))

            # --- Bulk accepting a DataFrame (id column auto-detected) ----------
            step("forcetime: bulk from DataFrame (id column auto-detected)",
                 lambda: GetForceTimeBulk(test_ids=ids_source.head(HD_BULK_LIMIT)))

            # --- Bulk with NO ids: delegates to GetTests(**kwargs) -------------
            step("forcetime: bulk via GetTests delegation (typeId + from_)",
                 lambda: GetForceTimeBulk(typeId="CMJ", from_=HD_FROM_RECENT))

            # --- Export to CSV --------------------------------------------------
            import tempfile
            _csv_dir = os.path.join(tempfile.gettempdir(), "hdforce_smoke_csv")
            def _export_csv():
                paths = GetForceTimeBulk(test_ids=_bulk_ids, export=True,
                                         export_dir=_csv_dir, format="csv")
                print(f"    wrote {len(paths)} file(s) to {_csv_dir}")
                return paths
            step("forcetime: bulk export -> CSV", _export_csv)

            # --- Export to JSON -------------------------------------------------
            _json_dir = os.path.join(tempfile.gettempdir(), "hdforce_smoke_json")
            step("forcetime: bulk export -> JSON",
                 lambda: GetForceTimeBulk(test_ids=_bulk_ids, export=True,
                                          export_dir=_json_dir, format="json"))

            # --- Export with de-identification ----------------------------------
            _deid_dir = os.path.join(tempfile.gettempdir(), "hdforce_smoke_deid")
            step("forcetime: bulk export -> CSV, de-identified",
                 lambda: GetForceTimeBulk(test_ids=_bulk_ids, export=True,
                                          export_dir=_deid_dir, format="csv",
                                          deidentify=True))

            # --- Parquet export (only if a parquet engine is installed) ---------
            _has_parquet = (importlib.util.find_spec("pyarrow") is not None
                            or importlib.util.find_spec("fastparquet") is not None)
            if _has_parquet:
                _pq_dir = os.path.join(tempfile.gettempdir(), "hdforce_smoke_parquet")
                step("forcetime: bulk export -> Parquet",
                     lambda: GetForceTimeBulk(test_ids=_bulk_ids, export=True,
                                              export_dir=_pq_dir, format="parquet"))
            else:
                step_skip("forcetime: bulk export -> Parquet",
                          "no parquet engine (pyarrow/fastparquet) installed")

        else:
            step_skip("forcetime: all scenarios", "no test trials available to sample")

    else:
        step_skip("forcetime: all scenarios", "no connection")


    # =============================================================================
    # 9b. CENTER OF PRESSURE  (network)  —  Free Run tests only
    # =============================================================================
    # COP data is exclusive to the Free Run test type. Locate a Free Run trial
    # dynamically (skip cleanly if the org has none), then exercise GetCOP(): the
    # DataFrame shape, the seven columns, and the nullable COP series (NaN where no
    # weight is on a plate). Mirrors the COP section of hawkinR's smoke_test.R.

    if CONNECTED:
        _free_run = GetTests(from_=HD_FROM_WIDE, to_=HD_TO, typeId="Free Run")
        _free_run_id = None
        if isinstance(_free_run, pd.DataFrame) and len(_free_run) > 0 \
                and "id" in _free_run.columns:
            _free_run_id = _free_run["id"].iloc[0]

        if _free_run_id is not None:

            # --- Single COP trial ----------------------------------------------
            def _single_cop():
                cop = GetCOP(testId=_free_run_id)
                print(f"    athlete={cop.attrs.get('Athlete Name')}  "
                      f"samples={len(cop)}  columns={list(cop.columns)}")
                return cop
            step(f"cop: single Free Run trial ({_free_run_id})", _single_cop)

            # --- DataFrame shape: 7 columns present, time axis never NaN --------
            def _cop_shape():
                cop = GetCOP(testId=_free_run_id)
                expected = ["time", "copX", "copY", "leftCopX", "leftCopY",
                            "rightCopX", "rightCopY"]
                missing = [c for c in expected if c not in cop.columns]
                if missing:
                    raise AssertionError(f"missing COP columns: {missing}")
                if len(cop) == 0:
                    raise AssertionError("COP DataFrame is empty")
                if cop["time"].isna().any():
                    raise AssertionError("time should never contain NaN")
                if cop.attrs.get("Test ID") != _free_run_id:
                    raise AssertionError("Test ID attr mismatch")
                return cop
            step("cop: DataFrame shape + nullable COP series", _cop_shape)
        else:
            step_skip("cop: single Free Run trial", "no Free Run tests in org")
            step_skip("cop: DataFrame shape + nullable COP series",
                      "no Free Run tests in org")
    else:
        step_skip("cop: all scenarios", "no connection")


    # =============================================================================
    # 10. WRITE OPERATIONS  (network, OPT-IN)  —  create + update athletes
    # =============================================================================
    # These mutate your org. Guarded by RUN_WRITE_TESTS. A uniquely-named
    # SMOKETEST_* athlete is created, then immediately deactivated. There is no
    # delete endpoint, so cleanup = deactivation.

    if CONNECTED and RUN_WRITE_TESTS:

        smoke_name = "SMOKETEST_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        created_id = {"value": None}

        def _create():
            results = CreateAthletes([NewAthlete(name=smoke_name, active=True)])
            hit = next((r for r in results if r.name == smoke_name and r.successful), None)
            if hit and hit.id:
                created_id["value"] = hit.id
            else:
                # Fall back to a roster lookup if the create response lacked the id.
                roster = GetAthletes(includeInactive=True)
                match = roster[roster["name"] == smoke_name]
                if len(match) > 0:
                    created_id["value"] = match["id"].iloc[0]
            return results

        step(f"write: CreateAthletes ({smoke_name})", _create)

        if created_id["value"]:
            step(f"write: UpdateAthletes ({smoke_name} -> active=False)",
                 lambda: UpdateAthletes([Athlete(
                     id=created_id["value"], name=smoke_name, active=False)]))
        else:
            step_skip("write: UpdateAthletes", "could not resolve created athlete id")

    else:
        step_skip("write: create/update athletes",
                  "no connection" if not CONNECTED else "RUN_WRITE_TESTS is False")


    # =============================================================================
    # 11. EXPECTED-ERROR PATHS
    # =============================================================================
    # These should RAISE — and that raise is the PASS.

    # GetForceTime rejects a non-string id before any network call.
    step_expect_error("error: GetForceTime() rejects non-string testId",
                      lambda: GetForceTime(testId=12345),
                      pattern=r"must be a string")

    if CONNECTED:
        # A bogus trial id: API returns 200 with an empty body -> ValueError.
        step_expect_error("error: GetForceTime() with bogus id",
                          lambda: GetForceTime(testId="does-not-exist-000000000000"),
                          pattern=r"No force-time data|Error")

        # Two entity filters at once is rejected client-side.
        step_expect_error("error: GetTests() rejects two filters at once",
                          lambda: GetTests(from_=HD_FROM_RECENT,
                                           athleteId="x", teamId="y"),
                          pattern=r"Only one of")

        # Unknown typeId is rejected client-side.
        step_expect_error("error: GetTests() rejects unknown typeId",
                          lambda: GetTests(from_=HD_FROM_RECENT, typeId="NotARealType"),
                          pattern=r"typeId incorrect")

        # A bogus COP id surfaces as an error (no COP data / not found).
        step_expect_error("error: GetCOP() with bogus id",
                          lambda: GetCOP(testId="does-not-exist-000000000000"),
                          pattern=r"404|[Nn]ot [Ff]ound|No COP|COP|Error")

        # COP is Free Run only: requesting it for a non-Free-Run test must error.
        _cmj = GetTests(from_=HD_FROM_WIDE, to_=HD_TO, typeId="CMJ")
        _cmj_id = (_cmj["id"].iloc[0]
                   if isinstance(_cmj, pd.DataFrame) and len(_cmj) > 0
                   and "id" in _cmj.columns else None)
        if _cmj_id:
            step_expect_error("error: GetCOP() on a non-Free-Run test (CMJ)",
                              lambda: GetCOP(testId=_cmj_id),
                              pattern=r"404|[Nn]ot [Ff]ound|Free Run|No COP|COP|Error")
        else:
            step_skip("error: GetCOP() on a non-Free-Run test", "no CMJ tests in org")
    else:
        step_skip("error: network error paths", "no connection")


    # =============================================================================
    # 12. TOKEN REFRESH  (network)
    # =============================================================================
    # Force the access token to look expired, then make a call. ensure_token()
    # should transparently re-authenticate before the request succeeds.
    #
    # This trick relies on os.environ['TOKEN_EXPIRATION'] being the source of
    # truth, which is true for the "env" and "manual" methods. For "file", the
    # expiration is read back from the .env file, so we skip there.

    if CONNECTED and HD_AUTH_METHOD in ("env", "manual"):
        def _force_refresh():
            os.environ["TOKEN_EXPIRATION"] = str(int(time.time()) - 10)  # pretend expired
            return GetTeams()  # should trigger a refresh first
        step("auth: forced token refresh on next call", _force_refresh)
    elif CONNECTED:
        step_skip("auth: forced token refresh",
                  "file method reads expiration from disk; cannot force via os.environ")
    else:
        step_skip("auth: forced token refresh", "no connection")


    # =============================================================================
    # 13. SUMMARY
    # =============================================================================

    n_pass = sum(1 for r in _RESULTS if r["status"] == "PASS")
    n_fail = sum(1 for r in _RESULTS if r["status"] == "FAIL")
    n_skip = sum(1 for r in _RESULTS if r["status"] == "SKIP")
    total_time = sum(r["elapsed_s"] or 0 for r in _RESULTS)

    print("\n\n================== SMOKE TEST SUMMARY ==================")
    _w = max((len(r["step"]) for r in _RESULTS), default=4)
    for r in _RESULTS:
        rows = "" if r["rows"] is None else str(r["rows"])
        secs = "" if r["elapsed_s"] is None else f"{r['elapsed_s']}s"
        print(f"  {r['status']:<4}  {r['step']:<{_w}}  {rows:>6}  {secs}")
    print("-------------------------------------------------------")
    print(f"PASS: {n_pass}   FAIL: {n_fail}   SKIP: {n_skip}   (of {len(_RESULTS)} steps)")
    print(f"Total time: {total_time:.1f}s")

    if n_fail:
        print("\nFailures:")
        for r in _RESULTS:
            if r["status"] == "FAIL":
                print(f"  - {r['step']}\n      {r['detail']}")
    print("=======================================================")

    # Persist the results table next to the log file.
    results_csv = re.sub(r"\.log$", "", HD_LOG_FILE) + "_results.csv"
    try:
        with open(results_csv, "w", newline="") as fh:
            writer = csv.DictWriter(
                fh, fieldnames=["step", "status", "rows", "elapsed_s", "detail"])
            writer.writeheader()
            writer.writerows(_RESULTS)
        print(f"\nResults written to: {results_csv}")
        if HD_LOG_TO_FILE:
            print(f"Full trace log:     {HD_LOG_FILE}")
    except Exception as e:  # pragma: no cover
        print(f"\nCould not write results CSV: {e}")

    # Non-zero exit code if anything failed, so CI can gate on it.
    sys.exit(1 if n_fail else 0)


if __name__ == "__main__":
    main()
