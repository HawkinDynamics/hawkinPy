"""Network-free tests for the useNulls / rounding / nestMetrics query params
(API v1.16) and the response shapes they produce.

These do not hit the API: `ensure_token` and `requests.get` are patched so the
tests exercise query construction and `responseHandler` only.
"""
import importlib

import pandas as pd
import pytest

get_tests_module = importlib.import_module("hdforce.GetTests")
from hdforce.GetTests import GetTests
from hdforce.utils import responseHandler


ATHLETE = {
    "id": "a1",
    "name": "Alex Athlete",
    "teams": ["team1"],
    "groups": [],
    "active": True,
    "external": {},
}
TEST_TYPE = {"id": "tt1", "name": "Countermovement Jump", "canonicalId": "c1", "tags": []}


def _envelope(records):
    return {
        "data": records,
        "count": len(records),
        "lastSyncTime": 100,
        "lastTestTime": 90,
        "nextCursor": None,
    }


FLAT_NA = _envelope([
    {
        "id": "t1",
        "timestamp": 1,
        "segment": "Countermovement Jump:1",
        "active": True,
        "athlete": ATHLETE,
        "testType": TEST_TYPE,
        "Jump Height(m)": "N/A",
        "System Weight(N)": 800.5,
    }
])

NESTED = _envelope([
    {
        "id": "t1",
        "timestamp": 1,
        "segment": "Countermovement Jump:1",
        "active": True,
        "athlete": ATHLETE,
        "testType": TEST_TYPE,
        "metrics": [
            {"metricId": "jumpHeight", "metricLabel": "Jump Height",
             "metricUnits": "m", "metricValue": 0.4123},
            {"metricId": "weight", "metricLabel": "System Weight",
             "metricUnits": "N", "metricValue": 800.5},
        ],
    },
    {
        "id": "t2",
        "timestamp": 2,
        "segment": "Countermovement Jump:2",
        "active": True,
        "athlete": ATHLETE,
        "testType": TEST_TYPE,
        "metrics": [],
    },
])


# ----- responseHandler shapes -----------------------------------------------

def test_flat_response_preserves_na_strings_when_useNulls_false():
    df = responseHandler(FLAT_NA)

    assert len(df) == 1
    assert df.loc[0, "jump_height_m"] == "N/A"
    assert df.loc[0, "system_weight_n"] == 800.5


def test_nested_response_becomes_long_table():
    df = responseHandler(NESTED)

    # One row per test x metric; a test with no numeric metrics keeps one row.
    assert len(df) == 3
    for col in ("metric_id", "metric_label", "metric_units", "metric_value"):
        assert col in df.columns
    assert "metrics" not in df.columns

    t1 = df[df["id"] == "t1"]
    assert list(t1["metric_id"]) == ["jumpHeight", "weight"]
    assert list(t1["metric_label"]) == ["Jump Height", "System Weight"]
    assert list(t1["metric_units"]) == ["m", "N"]
    assert list(t1["metric_value"]) == [0.4123, 800.5]

    t2 = df[df["id"] == "t2"]
    assert len(t2) == 1
    assert pd.isna(t2["metric_id"].iloc[0])

    # Trial / athlete / test-type columns are carried onto every metric row.
    assert (t1["athlete_name"] == "Alex Athlete").all()
    assert (t1["testType_name"] == "Countermovement Jump").all()
    assert (t1["segment"] == "Countermovement Jump:1").all()


# ----- GetTests query emission ----------------------------------------------

class _FakeResponse:
    status_code = 200
    reason = "OK"

    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


@pytest.fixture
def capture_query(monkeypatch):
    calls = []

    def fake_get(url, headers=None, params=None):
        calls.append(dict(params))
        return _FakeResponse(_envelope([]))

    monkeypatch.setenv("CLOUD_URL", "https://example.test/api/v1")
    monkeypatch.setattr(get_tests_module, "ensure_token", lambda: "tok")
    monkeypatch.setattr(get_tests_module.requests, "get", fake_get)
    return calls


def test_defaults_emit_no_shape_params(capture_query):
    GetTests(from_=1690859091)

    q = capture_query[0]
    assert "useNulls" not in q
    assert "rounding" not in q
    assert "nestMetrics" not in q


def test_non_default_shape_params_are_emitted(capture_query):
    GetTests(from_=1690859091, useNulls=False, rounding=True, nestMetrics=True)

    q = capture_query[0]
    assert q["useNulls"] == "false"
    assert q["rounding"] == "true"
    assert q["nestMetrics"] == "true"


def test_default_true_useNulls_is_not_sent_as_true(capture_query):
    # Sending nothing keeps the API default; we never send `useNulls=true`.
    GetTests(from_=1690859091, useNulls=True, rounding=False, nestMetrics=False)

    q = capture_query[0]
    assert "useNulls" not in q
    assert "rounding" not in q
    assert "nestMetrics" not in q
