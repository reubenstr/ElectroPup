""" 
   
"""

import os
import math
import yaml
import numpy as np

class FrameParameters:
    def __init__(self, frame_parameters_filepath):

        self.error = False

        try:
            if os.path.exists(frame_parameters_filepath):
                with open(frame_parameters_filepath, 'r') as stream:
                    frame_parameters = yaml.safe_load(stream)
            else:
                print(f"[Frame] parameter file not found! Filepath: {frame_parameters_filepath}")
        except:
             self.error = True

        # Frame dimensions:
        self.hip_length = frame_parameters['hip_length']
        self.upper_leg_length = frame_parameters['upper_leg_length']
        self.lower_leg_length = frame_parameters['lower_leg_length']
        self.body_width = frame_parameters['body_width']
        self.body_length = frame_parameters['body_length']
        self.foot_length = frame_parameters['foot_length']
        self.foot_width = frame_parameters['foot_width']

        # Joint bounds:
        self.abduction_joint_lower_bounds = math.radians(frame_parameters['abduction_joint_lower_bounds'])
        self.abduction_joint_upper_bounds = math.radians(frame_parameters['abduction_joint_upper_bounds'])
        self.hip_joint_lower_bounds = math.radians(frame_parameters['hip_joint_lower_bounds'])
        self.hip_joint_upper_bounds = math.radians(frame_parameters['hip_joint_upper_bounds'])
        self.knee_joint_lower_bounds = math.radians(frame_parameters['knee_joint_lower_bounds'])
        self.knee_joint_upper_bounds = math.radians(frame_parameters['knee_joint_upper_bounds'])

    def hasError(self):
        return self.error
