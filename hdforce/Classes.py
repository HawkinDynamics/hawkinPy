from typing import List, Dict, Optional
from pydantic import BaseModel

# Athlete Class


class NewAthlete(BaseModel):
    # Required
    name: str
    active: bool = True
    # Optional
    teams: List[str] = []
    groups: List[str] = []
    external: Dict = {}

# -------------------- #
# Athlete Class


class Athlete(BaseModel):
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
    # absent and None to None here.
    image: Optional[str] = None
    position: Optional[str] = None
    dob: Optional[str] = None
    sport: Optional[str] = None
    # Centimeters, range [1, 300] when present.
    height: Optional[float] = None
    # Unix epoch milliseconds of the athlete's most recent test session.
    lastTestedOn: Optional[int] = None

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
