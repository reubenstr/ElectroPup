
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

    GAIT_CRAWL = "gait_crawl"
    GAIT_TROT = "gait_trot"
    GAIT_RUN = "gait_run"
    GAIT_CLIMB= "gait_climb"

    GAMEPAD_INPUT = "gamepad_input"
    TOUCH_INPUT = "touch_input"

    WIFI_AS_CLIENT = "wifi_as_client"
    WIFI_AS_HOTSPOT = "wifi_as_hotspot"

@dataclass
class TouchMessage:
    leftX: float
    leftY: float
    rightX: float
    rightY: float
    command: InputCommand