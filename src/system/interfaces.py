
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
    DISABLE_ENABLE_MOTORS = "disable_enable_motors"
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

    IDLE = "idle"

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



