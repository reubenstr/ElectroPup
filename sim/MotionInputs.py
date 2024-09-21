""" 
    Data class containing motion parameters controlling
    the quadruped's movement and states.
"""

import numpy as np
import copy
from dataclasses import dataclass
from enum import Enum


class MotionState(Enum):
    POSE = 1
    MOTION = 2

@dataclass
class MotionInputs:
    motion_state = MotionState.POSE
    pos: np.ndarray = np.array([0.0, 0.0, 0.0])
    orn: np.ndarray = np.array([0.0, 0.0, 0.0])
    step_length: float = 0.0  
    yaw_rate: float = 0.0  

    def print(self):
        print(f"Motion State: {self.motion_state}")
        print(f"Pos: {self.pos}")
        print(f"orn: {self.orn}")

