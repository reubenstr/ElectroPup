from enum import Enum


class AxesMap(Enum):
    LEFT_X = 0
    LEFT_Y = 1
    L2 = 2
    RIGHT_X = 3
    RIGHT_Y = 4
    R2 = 5
    DPAD_X = 6
    DPAD_Y = 7

class ButtonMap(Enum):
    CROSS = 0
    CIRCLE = 1
    TRIANGLE = 2
    SQUARE = 3
    L1 = 4
    R1 = 5
    L2 = 6
    R2 = 7
    SHARE = 8
    OPTIONS = 9
    PS = 10
    L3 = 11
    R3 = 12