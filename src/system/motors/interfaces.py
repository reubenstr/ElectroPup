from enum import IntEnum, Enum, StrEnum
from dataclasses import dataclass

class MotorSpeeds(IntEnum):
    SLOW = 1000
    MOTION = 2000


class MotorName(StrEnum):
    FLA = 'FLA'
    FLH = 'FLH'
    FLK = 'FLK'
    FRA = 'FRA'
    FRH = 'FRH'
    FRK = 'FRK'
    BLA = 'BLA'
    BLH = 'BLH'
    BLK = 'BLK'
    BRA = 'BRA'
    BRH = 'BRH'
    BRK = 'BRK'

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

