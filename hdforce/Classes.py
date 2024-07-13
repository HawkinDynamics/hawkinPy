from typing import List, Dict
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
