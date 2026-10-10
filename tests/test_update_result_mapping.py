"""Network-free tests for how UpdateAthletes maps API results back onto input.

These do not hit the API: `ensure_token` and `requests.put` are patched, so the
tests exercise result attribution only.

Two athletes in one batch can share a name — common surnames, or a roster
imported twice — so results are keyed on `id`, which `Athlete` requires and the
API returns on success and echoes in `failures[].data`.
"""
from unittest.mock import MagicMock, patch

import pytest

from hdforce.Classes import Athlete
from hdforce.UpdateAthletes import UpdateAthletes


def _response(data=None, failures=None):
    return MagicMock(
        status_code=200,
        json=lambda: {"data": data or [], "failures": failures or []},
    )


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    monkeypatch.setenv("CLOUD_URL", "https://example.invalid/api/v1")
    with patch("hdforce.UpdateAthletes.ensure_token", return_value="tok"):
        yield


@patch("hdforce.UpdateAthletes.requests.put")
def test_same_name_different_ids_get_their_own_results(mock_put):
    """The failure belongs to id_2 alone; id_1 updated fine."""
    mock_put.return_value = _response(
        data=[{"name": "Jordan Smith", "id": "id_1"}],
        failures=[{
            "reason": "Duplicate or Invalid Athlete Name",
            "data": {"name": "Jordan Smith", "id": "id_2"},
        }],
    )

    results = UpdateAthletes([
        Athlete(id="id_1", name="Jordan Smith"),
        Athlete(id="id_2", name="Jordan Smith"),
    ])

    by_id = {r.id: r for r in results}
    assert by_id["id_1"].successful is True
    assert by_id["id_1"].reason == []
    assert by_id["id_2"].successful is False
    assert by_id["id_2"].reason == ["Duplicate or Invalid Athlete Name"]


@patch("hdforce.UpdateAthletes.requests.put")
def test_each_failure_reason_lands_on_its_own_athlete(mock_put):
    mock_put.return_value = _response(failures=[
        {"reason": "Invalid height", "data": {"name": "Sam Lee", "id": "id_1"}},
        {"reason": "Invalid dob", "data": {"name": "Sam Lee", "id": "id_2"}},
    ])

    results = UpdateAthletes([
        Athlete(id="id_1", name="Sam Lee"),
        Athlete(id="id_2", name="Sam Lee"),
    ])

    assert [r.reason for r in results] == [["Invalid height"], ["Invalid dob"]]
    assert all(r.successful is False for r in results)


@patch("hdforce.UpdateAthletes.requests.put")
def test_falls_back_to_name_when_a_response_entry_has_no_id(mock_put):
    """Older or partial responses without ids still attribute by name."""
    mock_put.return_value = _response(
        data=[{"name": "Ada"}],
        failures=[{"reason": "Invalid height", "data": {"name": "Grace"}}],
    )

    results = UpdateAthletes([
        Athlete(id="id_1", name="Ada"),
        Athlete(id="id_2", name="Grace"),
    ])

    assert results[0].successful is True
    assert results[1].successful is False
    assert results[1].reason == ["Invalid height"]


@patch("hdforce.UpdateAthletes.requests.put")
def test_mixed_response_never_reports_a_rejected_athlete_successful(mock_put):
    """A success entry without an id must not vouch for a same-named athlete
    the failures list rejected by id. The API returns ids all-or-nothing, so
    this shape shouldn't occur; an unknown error beats a false success."""
    mock_put.return_value = _response(
        data=[{"name": "Jordan Smith"}],
        failures=[{
            "reason": "Invalid height",
            "data": {"name": "Jordan Smith", "id": "id_2"},
        }],
    )

    results = UpdateAthletes([
        Athlete(id="id_1", name="Jordan Smith"),
        Athlete(id="id_2", name="Jordan Smith"),
    ])

    by_id = {r.id: r for r in results}
    assert by_id["id_2"].successful is False
    assert by_id["id_2"].reason == ["Invalid height"]
    assert by_id["id_1"].successful is False
    assert by_id["id_1"].reason == ["Unknown error"]


@patch("hdforce.UpdateAthletes.requests.put")
def test_athlete_missing_from_the_response_is_an_unknown_error(mock_put):
    mock_put.return_value = _response()

    results = UpdateAthletes([Athlete(id="id_1", name="Ada")])

    assert results[0].successful is False
    assert results[0].reason == ["Unknown error"]
