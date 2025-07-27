"""
Class containing motion parameters for quadruped rotation, translation
"""

import copy
import numpy as np
from enum import Enum
from dataclasses import dataclass
from math import degrees, atan2, sqrt


@dataclass
class MotionParameters:
    ###############################################################################
    # Rotation limits parameters (degrees)
    ###############################################################################
    roll_min: float = -30.0
    roll_max: float = 30.0
    pitch_min: float = -30.0
    pitch_max: float = 30.0
    yaw_min: float = -30.0
    yaw_max: float = 30.0


    ###############################################################################
    # Gait parameters parameters
    ###############################################################################
    '''lateral_fraction: float = 0.0
    step_velocity: float = 0.001
    swing_period: float = 0.200
    clearance_height: float = 0.045
    penetration_depth: float = 0.003
    yaw_rate_min: float = -0.785
    yaw_rate_max: float = 0.785
    step_length_min: float = -0.100
    step_length_max: float = 0.100'''

    ###############################################################################
    # Running values, do not change, will be overwritten
    ###############################################################################
    roll: float = 0
    pitch: float = 0
    yaw: float = 0
    side_translation: float = 0
    forward_translation: float = 0
    height_translation: float = 0
    step_length: float = 0
    yaw_rate: float = 0


    ###############################################################################
    # Call from the Input class to set values
    ###############################################################################

    def update_forward_raw(self, value : float):
        self.forward_raw = value
    
    def update_heading_x(self, value: float):
        self._heading_x = value
        self.heading_raw = value

    def update_heading_y(self, value: float):
        self._heading_y = value

    ###############################################################################
    # Getters / Setters
    ###############################################################################

    def get_forward_raw(self) -> float:
        """
        Returns value ranged -1.0 to 1.0 representing an gamepad axis
        """
        return self.forward_raw   
    
    def get_forward_direction(self) -> bool:       
        return True if self.forward_raw > 0 else False
       
    def get_heading_raw(self) -> float:
        """
        Returns value ranged -1.0 to 1.0 representing an gamepad axis
        """
        return self.heading_raw

    def get_heading_degrees(self):
        return degrees(atan2(self._heading_x, self._heading_y))

    def get_heading_magnitude(self):
        return sqrt((self._heading_x) ** 2 + (self._heading_y) ** 2)




###############################################################################
# Premade Positions
###############################################################################

def get_pose_standing(self):
    motion_parameters = copy.deepcopy(self)
    motion_parameters.roll = 0
    motion_parameters.pitch = 0
    motion_parameters.yaw = 0
    motion_parameters.side_translation = 0
    motion_parameters.forward_translation = 0
    motion_parameters.height_translation = (MotionParameters.height_translation_min + MotionParameters.height_translation_max) / 2
    motion_parameters.step_length = 0
    motion_parameters.yaw_rate = 0
    return motion_parameters

def get_pose_lie_down(self):
    motion_parameters = copy.deepcopy(self)
    motion_parameters.roll = 0
    motion_parameters.pitch = 0
    motion_parameters.yaw = 0
    motion_parameters.side_translation = 0
    motion_parameters.forward_translation = 0
    motion_parameters.height_translation = MotionParameters.height_translation_min
    motion_parameters.step_length = 0
    motion_parameters.yaw_rate = 0
    return motion_parameters

