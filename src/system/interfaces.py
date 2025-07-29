import can
from threading import Thread, Lock, Event
from dataclasses import dataclass
from enum import Enum, StrEnum, IntEnum


class OpModes(StrEnum):
    NA = "N/A"
    LIVE = "live"
    SIM = "sim"


class InputMode(StrEnum):
    NA = "N/A"
    GAMEPAD = "gamepad"
    TOUCH = "touch"


# Commands from the touch and gamepad inputs
class InputCommand(StrEnum):
    NO_UPDATE = "no_update"
    E_STOP = "e_stop"
    CLEAR_ERRORS = "clear_errors"

    SIT = "sit"
    STAND = "stand"
    POSE = "pose"
    WALK = "walk"

    GAIT_WALK = "gait_walk"
    GAIT_TROT = "gait_trot"

    GAMEPAD_INPUT = "gamepad_input"
    TOUCH_INPUT = "touch_input"


class MotorSpeeds(IntEnum):
    STAND = 1
    SIT = 1
    MOTION = 10


class MotorCurrents(IntEnum):
    STAND = 1
    SIT = 1
    MOTION = 3


class Status(StrEnum):
    NONE = "none"
    STANDBY = "standby"
    ACTIVE = "active"
    WARNING = "warning"
    CRITICAL = "critical"
    ERROR = "error"


class MotionState(StrEnum):
    NONE = "none"
    STANDBY = "standby"   
   
    STAND = "stand"
    SIT = "sit"
    POSE = "pose"
    WALK = "walk"

    TRANSITION = "transition"


class StandStates(StrEnum):
    NONE = "none"
    START = "start"
    LIFT_FEMUR = "lift_femur"
    LIFT_FOOT = "lift_foot"
    ROTATE_COXIA = "rotate_coxia"
    LOWER_FOOT = "lower_foot"
    PUSH_UP = "push_up"
    COMPLETE = "complete"


class Contacts:
    error: bool = False
    right_front: bool = False
    right_middle: bool = False
    right_back: bool = False
    left_front: bool = False
    left_middle: bool = False
    left_back: bool = False


@dataclass
class ImuData:
    roll: float
    pitch: float

    NONE = "none"
    STANDBY = "standby"
    ACTIVE = "active"
    WARNING = "warning"
    CRITICAL = "critical"
    ERROR = "error"


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
