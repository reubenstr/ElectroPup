""" 
  Class containing motion parameters for quadruped rotation, translation
"""

import os
import yaml
import math
import numpy as np
from enum import Enum

class KineticState(Enum):
    POSE = 1
    MOTION = 2
        
class ControllerEvent(Enum):
    KINETIC_STATE_TOGGLE = 1
    MOTOR_POWER_TOGGLE = 2
    

class MotionParameters: 
    def __init__(self, motion_parameters_filepath : str):
  
        if os.path.exists(motion_parameters_filepath):
            with open(motion_parameters_filepath, "r") as stream:
                motion_inputs = yaml.safe_load(stream)
                print(f"[MotionParameters] parameter file loaded, filepath: {motion_parameters_filepath}")
        else:
            print(f"[MotionParameters] parameter file not found, filepath: {motion_parameters_filepath}")
            raise FileNotFoundError

        #
        # Parameters
        #
        self.roll_min : float  = math.radians(motion_inputs["roll_min"])
        self.roll_max : float  = math.radians(motion_inputs["roll_max"])
        self.pitch_min : float  = math.radians(motion_inputs["pitch_min"])
        self.pitch_max : float  = math.radians(motion_inputs["pitch_max"])
        self.yaw_min : float  = math.radians(motion_inputs["yaw_min"])
        self.yaw_max : float  = math.radians(motion_inputs["yaw_max"])

        self.side_translation_min : float = motion_inputs["side_translation_min"]
        self.side_translation_max : float  = motion_inputs["side_translation_max"]
        self.foward_translation_min : float  = motion_inputs["foward_translation_min"]
        self.foward_translation_max : float  = motion_inputs["foward_translation_max"]
        self.height_translation_min : float  = motion_inputs["height_translation_min"]
        self.height_translation_max : float  = motion_inputs["height_translation_max"]

        self.lateral_fraction : float  = motion_inputs["lateral_fraction"]
        self.step_velocity : float  = motion_inputs["step_velocity"]
        self.swing_period : float  = motion_inputs["swing_period"]
        self.clearance_height : float  = motion_inputs["clearance_height"]
        self.penetration_depth : float  = motion_inputs["penetration_depth"]

        self.yaw_rate_min : float  = motion_inputs["yaw_rate_min"]
        self.yaw_rate_max : float  = motion_inputs["yaw_rate_max"]
        self.step_length_min : float  = motion_inputs["step_length_min"]
        self.step_length_max : float  = motion_inputs["step_length_max"]
     
        #
        # Values
        #        
        self.roll : float = 0
        self.pitch : float  = 0
        self.yaw : float  = 0
        self.side_translation : float = 0
        self.forward_translation : float  = 0
        self.height_translation : float  = 0
        self.step_length : float  = 0
        self.yaw_rate  : float = 0  


    ###############################################################################
    # Helpers
    ###############################################################################

    def print(self):
       print(self.roll, self.pitch, self.yaw, self.side_translation, self.forward_translation, self.height_translation) 