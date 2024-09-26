""" 
  Class containing motion parameters for quadruped rotation, translation, and states
"""

import os
import yaml
import math
import numpy as np
from enum import Enum

class MotionParameters:
    class MotionState(Enum):
        POSE = 1
        MOTION = 2

    def __init__(self, motion_parameters_filepath):

        self.error = False

        try:
            if os.path.exists(motion_parameters_filepath):
                with open(motion_parameters_filepath, "r") as stream:
                    motion_inputs = yaml.safe_load(stream)
                    print(f"[MotionParameters] parameter file loaded, filepath: {motion_parameters_filepath}")
            else:
                print(f"[MotionParameters] parameter file not found, filepath: {motion_parameters_filepath}")
        except:
            self.error = True

        #
        # Parameters
        #
        self.roll_min = math.radians(motion_inputs["roll_min"])
        self.roll_max = math.radians(motion_inputs["roll_max"])
        self.pitch_min = math.radians(motion_inputs["pitch_min"])
        self.pitch_max = math.radians(motion_inputs["pitch_max"])
        self.yaw_min = math.radians(motion_inputs["yaw_min"])
        self.yaw_max = math.radians(motion_inputs["yaw_max"])

        self.side_translation_min = motion_inputs["side_translation_min"]
        self.side_translation_max = motion_inputs["side_translation_max"]
        self.foward_translation_min = motion_inputs["foward_translation_min"]
        self.foward_translation_max = motion_inputs["foward_translation_max"]
        self.height_translation_min = motion_inputs["height_translation_min"]
        self.height_translation_max = motion_inputs["height_translation_max"]

        self.lateral_fraction = motion_inputs["lateral_fraction"]
        self.step_velocity = motion_inputs["step_velocity"]
        self.swing_period = motion_inputs["swing_period"]
        self.clearance_height = motion_inputs["clearance_height"]
        self.penetration_depth = motion_inputs["penetration_depth"]

        self.yaw_rate_min = motion_inputs["yaw_rate_min"]
        self.yaw_rate_max = motion_inputs["yaw_rate_max"]
        self.step_length_min = motion_inputs["step_length_min"]
        self.step_length_max = motion_inputs["step_length_max"]
     
        #
        # States and Values
        #
        self.motion_state = self.MotionState.POSE

        self.roll = 0
        self.pitch = 0
        self.yaw = 0
        self.side_translation = 0
        self.forward_translation = 0
        self.height_translation = 0

        self.step_length = 0
        self.yaw_rate = 0

    def is_error(self):
        return self.error

    def print(self):
       print(self.roll, self.pitch, self.yaw)
       

   
