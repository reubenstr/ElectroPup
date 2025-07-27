"""
Class containing motion parameters for quadruped rotation, translation
"""

import copy
import numpy as np
from enum import Enum
from dataclasses import dataclass


class KineticState(Enum):
    INIT = -1
    ERROR = 0
    STARTUP = 1
    HALT = 2
    STAND = 3
    LIE_DOWN = 4
    POSE = 5
    MOTION = 6
    FLIP = 7


class ControllerEvent(Enum):
    KINETIC_STATE_TOGGLE = 1
    MOTOR_POWER_TOGGLE = 2
    MOTOR_CLEAR_ERRORS = 3
    LIE_DOWN_AND_MOTORS_OFF = 4

@dataclass
class MotionParameters:
    ###############################################################################
    # Rotation limits (degrees)
    ###############################################################################
    roll_min: float = -30.0
    roll_max: float = 30.0
    pitch_min: float = -30.0
    pitch_max: float = 30.0
    yaw_min: float = -30.0
    yaw_max: float = 30.0

    ###############################################################################
    # Translation limits (meters)
    ###############################################################################

    side_translation_min: float = -0.050
    side_translation_max: float = 0.050
    foward_translation_min: float = -0.050
    foward_translation_max: float = 0.050

    # Lowest allowable point of body center in the world frame.
    height_translation_min: float = 0.050

    # Highest allowable position of body center, must no be higher than the physical leg lengths.
    height_translation_max: float = 0.250

    ###############################################################################
    # Gait parameters
    ###############################################################################
    lateral_fraction: float = 0.0
    step_velocity: float = 0.001
    swing_period: float = 0.200
    clearance_height: float = 0.045
    penetration_depth: float = 0.003
    yaw_rate_min: float = -0.785
    yaw_rate_max: float = 0.785
    step_length_min: float = -0.100
    step_length_max: float = 0.100

    ###############################################################################
    # Running values, do not change, will be overwritten
    ###############################################################################
    roll: float = 0
    pitch: float = 0
    yaw: float = 0
    side_translation: float = 0
    forward_translation: float = 0
    height_translation: float = (height_translation_min + height_translation_max) / 2
    step_length: float = 0
    yaw_rate: float = 0

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

