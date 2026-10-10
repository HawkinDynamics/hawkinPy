"""Network-free tests for writing athlete profile fields (position, sport, dob,
height) on create and update.

These do not hit the API: `ensure_token` and `requests.post` / `requests.put`
are patched so the tests exercise payload construction only.
"""
import warnings
from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from hdforce.Classes import Athlete, NewAthlete, athlete_payloads
from hdforce.CreateAthletes import CreateAthletes
from hdforce.UpdateAthletes import UpdateAthletes

PROFILE_FIELDS = ("position", "sport", "dob", "height")


def _ok_response(names):
    return MagicMock(
        status_code=200,
        json=lambda: {"data": [{"name": n, "id": f"id_{n}"} for n in names], "failures": []},
    )


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    monkeypatch.setenv("CLOUD_URL", "https://example.invalid/api/v1")
    with patch("hdforce.CreateAthletes.ensure_token", return_value="tok"), \
            patch("hdforce.UpdateAthletes.ensure_token", return_value="tok"):
        yield


# -------------------- #
# Create


@patch("hdforce.CreateAthletes.requests.post")
def test_create_sends_profile_fields_natively(mock_post):
    mock_post.return_value = _ok_response(["Jane"])
    CreateAthletes([NewAthlete(
        name="Jane", position="Forward", sport="Basketball",
        dob=date(1995, 3, 15), height=180.04,
        external={"Title": "Captain"},
    )])

    body = mock_post.call_args.kwargs["json"]
    assert mock_post.call_args.args[0] == "https://example.invalid/api/v1/athletes/bulk"
    assert body == [{
        "name": "Jane",
        "active": True,
        "teams": [],
        "groups": [],
        "external": {"Title": "Captain"},
        "position": "Forward",
        "sport": "Basketball",
        "dob": "1995-03-15",
        "height": 180.0,
    }]
    for field in PROFILE_FIELDS:
        assert field not in body[0]["external"]


@patch("hdforce.CreateAthletes.requests.post")
def test_create_omits_unset_profile_fields(mock_post):
    mock_post.return_value = _ok_response(["Jane"])
    CreateAthletes([NewAthlete(name="Jane")])

    body = mock_post.call_args.kwargs["json"]
    assert body == [{"name": "Jane", "active": True, "teams": [], "groups": [], "external": {}}]


def test_new_athlete_ignores_last_tested_on():
    payload = athlete_payloads([NewAthlete(name="Jane", lastTestedOn=1710000000)])
    assert "lastTestedOn" not in payload[0]


# -------------------- #
# Update


@patch("hdforce.UpdateAthletes.requests.put")
def test_update_sends_profile_fields_and_never_last_tested_on(mock_put):
    mock_put.return_value = _ok_response(["Jane"])
    UpdateAthletes([Athlete(
        id="a1", name="Jane", position="Guard", sport="Basketball",
        dob="1995", height=172.5, lastTestedOn=1710000000,
        external={"Title": "Captain"},
    )])

    body = mock_put.call_args.kwargs["json"]
    assert body == [{
        "id": "a1",
        "name": "Jane",
        "external": {"Title": "Captain"},
        "position": "Guard",
        "dob": "1995",
        "sport": "Basketball",
        "height": 172.5,
    }]


@patch("hdforce.UpdateAthletes.requests.put")
def test_update_omits_none_so_fields_stay_unchanged(mock_put):
    mock_put.return_value = _ok_response(["Jane"])
    UpdateAthletes([Athlete(id="a1", name="Jane", position=None, sport="", dob=None,
                            height=None, image=None, lastTestedOn=None)])

    body = mock_put.call_args.kwargs["json"][0]
    for field in PROFILE_FIELDS + ("image", "lastTestedOn"):
        assert field not in body
    # Nothing else was set either, so only id and name go out (CSE-151).
    assert body == {"id": "a1", "name": "Jane"}


# -------------------- #
# dob coercion


@pytest.mark.parametrize("value, expected", [
    (date(2001, 12, 31), "2001-12-31"),
    (datetime(2001, 12, 31, 23, 59), "2001-12-31"),
    ("2001-12-31", "2001-12-31"),
    (" 2001-02-03 ", "2001-02-03"),
    ("2001", "2001"),
    (2001, "2001"),
    ("", None),
    (None, None),
    (float("nan"), None),
])
def test_dob_accepted_formats(value, expected):
    assert NewAthlete(name="x", dob=value).dob == expected


@pytest.mark.parametrize("value", [
    "2001-02-30", "2001/02/03", "03-02-2001", "01", 101, True, 2001.0,
])
def test_dob_rejected_formats(value):
    with pytest.raises(ValidationError):
        NewAthlete(name="x", dob=value)


# -------------------- #
# height


def test_height_rounds_to_one_decimal():
    assert NewAthlete(name="x", height=180.26).height == 180.3
    assert Athlete(id="a", name="x", height="175").height == 175.0


@pytest.mark.parametrize("value", [float("inf"), True, "tall"])
def test_height_rejected(value):
    with pytest.raises(ValidationError):
        NewAthlete(name="x", height=value)


def test_height_nan_is_omitted():
    assert "height" not in athlete_payloads([NewAthlete(name="x", height=float("nan"))])[0]


@patch("hdforce.CreateAthletes.requests.post")
def test_height_below_100_warns_but_is_still_sent(mock_post):
    mock_post.return_value = _ok_response(["Jane"])
    with pytest.warns(UserWarning, match="Height below 100 cm sent for Jane"):
        CreateAthletes([NewAthlete(name="Jane", height=95)])
    assert mock_post.call_args.kwargs["json"][0]["height"] == 95.0


@patch("hdforce.UpdateAthletes.requests.put")
def test_height_at_or_above_100_does_not_warn(mock_put):
    mock_put.return_value = _ok_response(["Jane"])
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        UpdateAthletes([Athlete(id="a1", name="Jane", height=100)])


def test_height_zero_is_omitted_and_negative_is_left_to_the_api():
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        payload = athlete_payloads(
            [NewAthlete(name="zero", height=0), NewAthlete(name="neg", height=-5)]
        )
    assert "height" not in payload[0]
    # Out of range: sent for the API to reject, not reported as feet/inches.
    assert payload[1]["height"] == -5.0


@pytest.mark.parametrize("value", [999, "0999", "0999-01-01"])
def test_dob_year_below_1000_rejected_as_int_or_str(value):
    with pytest.raises(ValidationError):
        NewAthlete(name="x", dob=value)


def test_height_warning_is_aggregated():
    athletes = [NewAthlete(name=f"A{i}", height=90) for i in range(7)]
    with pytest.warns(UserWarning) as record:
        athlete_payloads(athletes)
    assert len(record) == 1
    assert "and 2 more" in str(record[0].message)


# -------------------- #
# position / sport


def test_blank_text_fields_are_omitted():
    payload = athlete_payloads([NewAthlete(name="x", position="   ", sport=float("nan"))])[0]
    assert "position" not in payload and "sport" not in payload


# -------------------- #
# Update sends only the fields the caller set (CSE-151)
#
# The API replaces each field it receives and leaves omitted fields unchanged,
# so sending the Athlete defaults would empty teams/groups, delete every custom
# property and re-activate an inactive athlete on a rename-only update.


@patch("hdforce.UpdateAthletes.requests.put")
def test_update_with_only_id_and_name_sends_only_those(mock_put):
    mock_put.return_value = _ok_response(["Jane"])
    UpdateAthletes([Athlete(id="a1", name="Jane")])

    body = mock_put.call_args.kwargs["json"]
    assert body == [{"id": "a1", "name": "Jane"}]


@patch("hdforce.UpdateAthletes.requests.put")
def test_update_sends_explicit_empty_and_default_values(mock_put):
    mock_put.return_value = _ok_response(["Jane", "Joe"])
    UpdateAthletes([
        Athlete(id="a1", name="Jane", teams=[], groups=[], external={}, active=False),
        Athlete(id="a2", name="Joe", active=True),
    ])

    body = mock_put.call_args.kwargs["json"]
    assert body == [
        {"id": "a1", "name": "Jane", "active": False, "teams": [], "groups": [], "external": {}},
        {"id": "a2", "name": "Joe", "active": True},
    ]


def test_update_sends_fields_assigned_or_mutated_after_construction():
    assigned = Athlete(id="a1", name="Jane")
    assigned.active = False
    mutated = Athlete(id="a2", name="Joe")
    mutated.teams.append("t1")
    mutated.external["Title"] = "Captain"

    payload = athlete_payloads([assigned, mutated])
    assert payload == [
        {"id": "a1", "name": "Jane", "active": False},
        {"id": "a2", "name": "Joe", "teams": ["t1"], "external": {"Title": "Captain"}},
    ]


def test_update_from_roster_row_sends_what_the_row_holds():
    # A GetAthletes() row turned into a dict: NaN profile columns, flattened
    # external.* columns (ignored by Athlete) and read-only lastTestedOn.
    row = {
        "id": "a1", "name": "Jane", "active": False, "teams": ["t1"], "groups": [],
        "external.Title": "Captain", "position": float("nan"), "sport": "Basketball",
        "dob": None, "height": float("nan"), "lastTestedOn": 1710000000,
    }
    payload = athlete_payloads([Athlete(**row)])
    assert payload == [{
        "id": "a1", "name": "Jane", "active": False, "teams": ["t1"], "groups": [],
        "sport": "Basketball",
    }]


@patch("hdforce.CreateAthletes.requests.post")
def test_create_still_sends_defaults(mock_post):
    mock_post.return_value = _ok_response(["Jane"])
    CreateAthletes([NewAthlete(name="Jane", sport="Rugby")])

    body = mock_post.call_args.kwargs["json"]
    assert body == [{
        "name": "Jane", "active": True, "teams": [], "groups": [], "external": {},
        "sport": "Rugby",
    }]


def test_mixed_create_and_update_payloads():
    payload = athlete_payloads([NewAthlete(name="New"), Athlete(id="a1", name="Old")])
    assert payload == [
        {"name": "New", "active": True, "teams": [], "groups": [], "external": {}},
        {"id": "a1", "name": "Old"},
    ]
