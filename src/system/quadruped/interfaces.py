
from enum import Enum

class LegName(Enum):
    FL = "FL"
    FR = "FR"
    BL = "BL"
    BR = "BR"

class QuadErrorState(Enum):
    NONE = 1
    KINEMATICS = 2
    JOINT = 3

class AngleUnits(Enum):
    DEGREES = 1
    RADIANS = 2
