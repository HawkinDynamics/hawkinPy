import math
import re
import warnings
from datetime import date, datetime
from typing import Annotated, Any, Dict, List, Optional
from pydantic import AfterValidator, BaseModel, BeforeValidator

# -------------------- #
# Athlete profile fields (position, sport, dob, height)
#
# Shared by NewAthlete (create) and Athlete (update). Each field is optional;
# None, NaN and blank strings all collapse to None so they are left out of the
# request body. On create an omitted field stays unset; on update it is left
# UNCHANGED -- the API cannot clear these fields (clear them in the Hawkin app).

# Heights below this many centimeters are reinterpreted by the API as legacy
# feet/inches when read back (e.g. 95 reads back as 241.3).
LEGACY_HEIGHT_THRESHOLD_CM = 100

# Read-only fields that the API ignores on write. Never sent.
READ_ONLY_ATHLETE_FIELDS = {"lastTestedOn"}

# Years 1000-9999, the same bound as an int year; the API checks the real range.
_DOB_PATTERN = re.compile(r"^[1-9]\d{3}(-\d{2}-\d{2})?$")


def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    return isinstance(value, str) and value.strip() == ""


def _profile_text(value: Any) -> Any:
    """position / sport: blank -> None, otherwise let pydantic validate str."""
    return None if _is_blank(value) else value


def _profile_dob(value: Any) -> Optional[str]:
    """dob: accept date/datetime, a 4-digit year (int or str) or 'YYYY-MM-DD'."""
    if _is_blank(value):
        return None
    if isinstance(value, bool):
        raise ValueError("dob must be a date, a 4-digit year, or 'YYYY-MM-DD'")
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, int):
        if 1000 <= value <= 9999:
            return str(value)
        raise ValueError(f"dob year must have 4 digits, got {value}")
    if isinstance(value, str):
        text = value.strip()
        if _DOB_PATTERN.match(text):
            if len(text) > 4:
                try:
                    date.fromisoformat(text)
                except ValueError:
                    raise ValueError(f"dob '{text}' is not a real calendar date")
            return text
        raise ValueError(f"dob must be 'YYYY' or 'YYYY-MM-DD', got '{value}'")
    raise ValueError(
        f"dob must be a date, a 4-digit year, or 'YYYY-MM-DD', got {type(value).__name__}"
    )


def _height_before(value: Any) -> Any:
    if _is_blank(value):
        return None
    if isinstance(value, bool):
        raise ValueError("height must be a number of centimeters")
    return value


def _height_after(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    if not math.isfinite(value):
        raise ValueError("height must be a finite number of centimeters")
    # 0 means "not provided" to the API; leave it out like None.
    return None if value == 0 else round(value, 1)


ProfileText = Annotated[Optional[str], BeforeValidator(_profile_text)]
DateOfBirth = Annotated[Optional[str], BeforeValidator(_profile_dob)]
HeightCm = Annotated[
    Optional[float], BeforeValidator(_height_before), AfterValidator(_height_after)
]

# -------------------- #
# Athlete Class


class NewAthlete(BaseModel):
    """An athlete to create with `CreateAthletes()`.

    Profile fields (all optional, sent as native fields, never in `external`):

    * position, sport: free text, trimmed by the API.
    * dob: `datetime.date`, a 4-digit year (int or str), or 'YYYY-MM-DD'.
      Sent as 'YYYY-MM-DD' or 'YYYY'.
    * height: centimeters, rounded to 1 decimal place. The API rejects values
      outside 0 to 300 (not checked here); 0 counts as not provided.
      Values below 100 are read back by the API as legacy feet/inches, so a
      warning is emitted when one is sent.

    Fields left as None (or blank) are not sent and stay unset.
    """
    # Required
    name: str
    active: bool = True
    # Optional
    teams: List[str] = []
    groups: List[str] = []
    external: Dict = {}
    position: ProfileText = None
    sport: ProfileText = None
    dob: DateOfBirth = None
    height: HeightCm = None

# -------------------- #
# Athlete Class


class Athlete(BaseModel):
    """An existing athlete, used with `UpdateAthletes()`.

    Only the fields you set are sent; every other field is left UNCHANGED.
    `Athlete(id=..., name="New Name")` renames the athlete without touching
    their `active` status, teams, groups or custom properties. A field you
    set explicitly is sent even when it equals the default, so `teams=[]`
    removes the athlete from all teams and `active=True` re-activates them.

    `position`, `sport`, `dob` and `height` follow the same rules as
    `NewAthlete`. Fields left as None (or blank) are not sent and are left
    UNCHANGED: the API cannot clear them, so clear them in the Hawkin app.
    `lastTestedOn` is read-only and is never sent. `external`, when you send
    it, still replaces all custom properties (not merged): any property you
    leave out of it is deleted.
    """
    # Required
    id: str
    name: str
    active: bool = True
    # Optional
    teams: List[str] = []
    groups: List[str] = []
    external: Dict = {}
    # image is three-state per the API: omitted = never set,
    # None = explicitly cleared, str = URL. Pydantic collapses
    # absent and None to None here, and None is not sent on write.
    image: Optional[str] = None
    position: ProfileText = None
    dob: DateOfBirth = None
    sport: ProfileText = None
    # Centimeters; the API rejects values outside 0 to 300. 0 is not sent.
    height: HeightCm = None
    # Unix epoch seconds of the athlete's most recent test session.
    # Read-only: never sent on write.
    lastTestedOn: Optional[int] = None

# -------------------- #
# Athlete write payloads


def _fields_to_send(athlete: BaseModel) -> Optional[set]:
    """Fields of an update (`Athlete`) to send; None means all (create).

    The API replaces each field it receives and leaves omitted fields
    unchanged, so an update sends only what the caller set: fields passed to
    the constructor or assigned later (`model_fields_set`), plus any default
    mutated in place (e.g. `athlete.teams.append(...)`), which pydantic does
    not track as set.
    """
    if not isinstance(athlete, Athlete):
        return None
    fields = set(athlete.model_fields_set)
    for name, info in type(athlete).model_fields.items():
        if name not in fields and not info.is_required():
            if getattr(athlete, name) != info.get_default(call_default_factory=True):
                fields.add(name)
    return fields


def athlete_payloads(athletes: List[BaseModel]) -> List[Dict[str, Any]]:
    """Build the JSON request body for the bulk create/update endpoints.

    On update (`Athlete`) only the fields the caller set are sent, so every
    other field (active, teams, groups, external, ...) is left unchanged. On
    create (`NewAthlete`) defaults are sent as before. None fields are always
    dropped (so omitted profile fields are unset on create and unchanged on
    update), read-only fields are never sent, and `external`, when sent, is
    passed through exactly as given. Emits a `UserWarning` if any athlete has
    a height below 100 cm.
    """
    payload = [
        athlete.model_dump(
            include=_fields_to_send(athlete),
            exclude_none=True,
            exclude=READ_ONLY_ATHLETE_FIELDS,
        )
        for athlete in athletes
    ]
    low = [
        p.get("name", "?") for p in payload
        if "height" in p and 0 < p["height"] < LEGACY_HEIGHT_THRESHOLD_CM
    ]
    if low:
        shown = ", ".join(low[:5]) + (f" and {len(low) - 5} more" if len(low) > 5 else "")
        warnings.warn(
            f"Height below {LEGACY_HEIGHT_THRESHOLD_CM} cm sent for {shown}. "
            "Height must be in centimeters; the Hawkin API reads values below "
            f"{LEGACY_HEIGHT_THRESHOLD_CM} back as legacy feet/inches "
            "(e.g. 95 reads back as 241.3).",
            UserWarning,
            stacklevel=3,
        )
    return payload

# -------------------- #
# Team Class


class Team(BaseModel):
    name: str
    id: str

# -------------------- #
# Group Class


class Group(BaseModel):
    name: str
    id: str

# -------------------- #
# Test Type Class


class TestType(BaseModel):
    name: str
    id: str

# -------------------- #
# Tags Class


class Tag(BaseModel):
    name: str
    id: str
    description: str

# -------------------- #
# AthleteResult Class
# AthleteResult Class


class AthleteResult(BaseModel):
    name: str
    successful: bool
    id: str
    reason: List[str] = []
