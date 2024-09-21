
'''
    Converts joystick axes and button input into motion parameters for robot control.

    Button map derived from Controllers.py in quad_gamepad/quad_gamepad/src
    
'''

import copy
import numpy as np
from motion_inputs import MotionInputs, MotionState
from gamepad_map import AxesMap, ButtonMap
           

class JoystickInterpreter():
    def __init__(self, motion_parameters):  
        self.motion_parameters = motion_parameters      
        self.mode_toggle_button_release_flag = True
        self.motion_inputs = MotionInputs()

    def map(self, n, in_min, in_max, out_min, out_max):
        return (n - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def get_motion_inputs(self, axes, buttons):
              
        # Reorient input axes
        axes[AxesMap.LEFT_Y.value] = -axes[AxesMap.LEFT_Y.value]
        axes[AxesMap.RIGHT_Y.value] = -axes[AxesMap.RIGHT_Y.value]

        # BUTTONS:
        if buttons[ButtonMap.TRIANGLE.value] == True and self.mode_toggle_button_release_flag == True:
            self.mode_toggle_button_release_flag = False
            if self.motion_inputs.motion_state == MotionState.MOTION:
                self.motion_inputs.motion_state = MotionState.POSE
            elif self.motion_inputs.motion_state == MotionState.POSE:
                self.motion_inputs.motion_state = MotionState.MOTION
        elif buttons[ButtonMap.TRIANGLE.value] == False:
            self.mode_toggle_button_release_flag = True

        # AXES:
        # pos: X, Y, Z coordinates
        # orn: Roll, Pitch, Yaw angles
        if self.motion_inputs.motion_state == MotionState.POSE:
                      
            self.motion_inputs.orn[0] = - self.map(
                axes[AxesMap.LEFT_X.value], -1, 1, self.motion_parameters['orn_x_min'], self.motion_parameters['orn_x_max'])
            self.motion_inputs.orn[1] = self.map(
                axes[AxesMap.LEFT_Y.value], -1, 1, self.motion_parameters['orn_y_min'], self.motion_parameters['orn_y_max'])
            self.motion_inputs.orn[2] = self.map(
                axes[AxesMap.RIGHT_X.value], -1, 1, self.motion_parameters['orn_z_min'], self.motion_parameters['orn_z_max'])
            self.motion_inputs.pos[2] = - self.map(
                axes[AxesMap.RIGHT_Y.value], -1, 1, self.motion_parameters['pos_z_min'], self.motion_parameters['pos_z_max'])
         
           
        if self.motion_inputs.motion_state == MotionState.MOTION:

            #self.motion_inputs.yaw_rate = self.map(
            #    axes[LEFT_X], -1, 1, self.motion_parameters['yaw_rate_min'], self.motion_parameters['yaw_rate_max'])
            self.motion_inputs.step_length = self.map(
                axes[AxesMap.LEFT_Y.value], -1, 1, self.motion_parameters['step_length_min'], self.motion_parameters['step_length_max'])          
            self.motion_inputs.yaw_rate = self.map(
               axes[AxesMap.RIGHT_X.value], -1, 1, self.motion_parameters['yaw_rate_min'], self.motion_parameters['yaw_rate_max'])            
            self.motion_inputs.pos[2] = - self.map(
                axes[AxesMap.RIGHT_Y.value], -1, 1, self.motion_parameters['pos_z_min'], self.motion_parameters['pos_z_max'])

        return copy.deepcopy(self.motion_inputs)

