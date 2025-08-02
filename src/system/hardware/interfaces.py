
from dataclasses import dataclass

@dataclass
class ImuData:
    roll: float
    pitch: float

@dataclass
class Contacts:
    error: bool = False
    right_front: bool = False
    right_middle: bool = False
    right_back: bool = False
    left_front: bool = False
    left_middle: bool = False
    left_back: bool = False
