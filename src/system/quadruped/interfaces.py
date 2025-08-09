
from enum import Enum, StrEnum
from typing import List, Dict, TypeAlias, Tuple
from quadruped.point import Point

Trajectory: TypeAlias = List[Point]
Trajectories: TypeAlias = List[Trajectory]

class LegName(StrEnum):
    FR = "FR"
    FL = "FL"
    BR = "BR"
    BL = "BL"

class JointName(StrEnum):
    ABDUCTION = "abduction"
    HIP = "hip"
    KNEE = "knee"

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
    

class OpMode(StrEnum):
    NA = "N/A"
    LIVE = "live"
    DEV = "dev"

class Status(StrEnum):
    NONE = "none"
    STANDBY = "standby"
    ACTIVE = "active"
    WARNING = "warning"
    CRITICAL = "critical"
    ERROR = "error"   