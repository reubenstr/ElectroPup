
import can
from threading import Thread, Lock, Event
from dataclasses import dataclass
from enum import Enum, StrEnum, IntEnum

class Status_x(StrEnum):
    NONE = 'none'
    STANDBY = 'standby'
    ACTIVE = 'active'
    WARNING = 'warning'
    CRITICAL = 'critical'
    ERROR = 'error'

class Status(IntEnum):
    NONE = 0
    STANDBY = 1
    ACTIVE = 2
    WARNING = 3
    CRITICAL =4
    ERROR = 5


@dataclass
class MotorInfo:  
    name:str
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