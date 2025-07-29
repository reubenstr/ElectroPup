from enum import IntEnum, Enum, auto
from dataclasses import dataclass

class MotorSpeeds(IntEnum):
    SLOW = 1000
    MOTION = 2000


class MotorName(Enum):
    FLA = auto()
    FLH = auto()
    FLK = auto()
    FRA = auto()
    FRH = auto()
    FRK = auto()
    BLA = auto()
    BLH = auto()
    BLK = auto()
    BRA = auto()
    BRH = auto()
    BRK = auto()


@dataclass
class MotorInfo:  
    name:MotorName
    can_channel: str
    id: int
    min_angle: float
    max_angle: float
    inverse_rotation: bool
    allow_motion: bool
    allow_comms: bool   

