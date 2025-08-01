import can
from threading import Thread, Lock, Event
from enum import IntEnum, Enum, StrEnum
from dataclasses import dataclass
from system.interfaces import Status


class MotorSpeeds(IntEnum):
    SLOW = 1000
    MOTION = 2000


class MotorName(StrEnum):
    FLA = "FLA"
    FLH = "FLH"
    FLK = "FLK"
    FRA = "FRA"
    FRH = "FRH"
    FRK = "FRK"
    BLA = "BLA"
    BLH = "BLH"
    BLK = "BLK"
    BRA = "BRA"
    BRH = "BRH"
    BRK = "BRK"


@dataclass
class MotorInfo:
    name: MotorName
    can_channel: str
    id: int
    min_angle: float
    max_angle: float
    inverse_rotation: bool
    allow_motion: bool
    allow_comms: bool


@dataclass
class CanInfo:
    can_channel: str
    bus: can.interface.Bus
    status: Status
    thread_handle: Thread
    lock: Lock
    exit_event: Event
    loop_completion_time_ms: float = 0.01
    worker_running_flag: bool = False

# For zeroing script.
@dataclass
class MotorZeroInfo:
    can_id: int
    motor_name: str
    motor_id: int
    allow_comms: bool
    allow_motion: bool
    position: float
    comms_error: bool   
    hardware_error: bool
    