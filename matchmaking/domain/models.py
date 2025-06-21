from enum import Enum
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
