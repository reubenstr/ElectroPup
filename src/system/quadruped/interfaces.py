
from enum import Enum, StrEnum
from typing import List, Dict, TypeAlias, Tuple
from quadruped.point import Point

Trajectory: TypeAlias = List[Point]
Trajectories: TypeAlias = List[Trajectory]

class LegName(Enum):
    FR = "FR"
    FL = "FL"
    BR = "BR"
    BL = "BL"

class QuadErrorState(Enum):
    NONE = 1
    KINEMATICS = 2
    JOINT = 3
    GROUND_PENETRATION = 4

class AngleUnits(Enum):
    DEGREES = 1
    RADIANS = 2

class MotionState(StrEnum):
    NONE = "none"
    STANDBY = "standby"
    STAND = "stand"
    SIT = "sit"
    POSE = "pose"
    WALK = "walk"   
    TRANSITION = "transition"
    