
from enum import Enum
from typing import List, Dict, TypeAlias, Tuple
from system.quadruped.point import Point

Trajectory: TypeAlias = List[Point]
Trajectories: TypeAlias = List[Trajectory]

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
