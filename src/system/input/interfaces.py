
from enum import StrEnum
from dataclasses import dataclass

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
    GAIT_RUN = "gait_run"

    GAMEPAD_INPUT = "gamepad_input"
    TOUCH_INPUT = "touch_input"

@dataclass
class TouchMessage:
    leftX: float
    leftY: float
    rightX: float
    rightY: float
    command: InputCommand