from enum import Enum
from typing import List
from pydantic import BaseModel

class Role(str, Enum):
    TANK = "TANK"
    HEALER = "HEALER"
    ASSASSIN = "ASSASSIN"
    BRUISER = "BRUISER"

class CharacterTemplate(BaseModel):
    id: int
    name: str
    role: Role

class Player(BaseModel):
    id: int
    name: str
    role: Role
    mmr: int

class Match(BaseModel):
    team_a: List[Player]
    team_b: List[Player]
    avg_mmr_a: float
    avg_mmr_b: float
