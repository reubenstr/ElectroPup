#!/usr/bin/env python3

"""
    Converts gamepad inputs into motion inputs.
"""

import os
import time
import yaml
import copy
from time import sleep

import Gamepad
from MotionInputs import MotionInputs, MotionState

class GamepadInterface:
    def __init__(self, motion_parameters):
        self.motion_parameters = motion_parameters
             
        self.motion_inputs = MotionInputs()   

    ###############################################################################
    # Methods
    ###############################################################################

    def connect_gamepad(self):
        # Find the ID of the connected joystick (gamepad): "ls /dev/input/ | grep js"
        joystick_id = 0  
        
        max_retries = 5
        retry = 0
        while not Gamepad.available(joystick_id):
            print("[GAMEPAD] not detected...")
            retry += 1
            if retry  > max_retries:
                return False
            time.sleep(1.0)
            
        print("[GAMEPAD] connected")
        self.gamepad = Gamepad.PS4(joystick_id)              
        self.gamepad.startBackgroundUpdates()
        return True

    def get_motion_inputs(self):
                 
        # BUTTONS:
        if self.gamepad.isPressed("TRIANGLE") == True and self.mode_toggle_button_release_flag == True:
            self.mode_toggle_button_release_flag = False
            if self.motion_inputs.motion_state == MotionState.MOTION:
                self.motion_inputs.motion_state = MotionState.POSE
            elif self.motion_inputs.motion_state == MotionState.POSE:
                self.motion_inputs.motion_state = MotionState.MOTION
        elif self.gamepad.isPressed("TRIANGLE") == False:
            self.mode_toggle_button_release_flag = True

            

        # AXES:
        # Joystick at up position generates negative values
        # Joystick at down position generates positive values
        # Inputs to map function reorientates values to up is positive and down is negative

        # Reorient input axes
        #axes[AxesMap.LEFT_Y.value] = -axes[AxesMap.LEFT_Y.value]
        #axes[AxesMap.RIGHT_Y.value] = -axes[AxesMap.RIGHT_Y.value]

        # pos: X, Y, Z coordinates
        # orn: Roll, Pitch, Yaw angles
        if self.motion_inputs.motion_state == MotionState.POSE:                      
            self.motion_inputs.orn[0] = self.map(
                self.gamepad.axis('LEFT-X'), -1, 1, self.motion_parameters['orn_x_min'], self.motion_parameters['orn_x_max'])
            self.motion_inputs.orn[1] = self.map(
               - self.gamepad.axis('LEFT-Y'), -1, 1, self.motion_parameters['orn_y_min'], self.motion_parameters['orn_y_max'])
            self.motion_inputs.orn[2] = self.map(
                self.gamepad.axis('RIGHT-X'), -1, 1, self.motion_parameters['orn_z_min'], self.motion_parameters['orn_z_max'])
            self.motion_inputs.pos[2] = self.map(
                - self.gamepad.axis('RIGHT-Y'), -1, 1, self.motion_parameters['pos_z_min'], self.motion_parameters['pos_z_max'])
           
           
        elif self.motion_inputs.motion_state == MotionState.MOTION:
            #self.motion_inputs.yaw_rate = self.map(
            #    axes[LEFT_X], -1, 1, self.motion_parameters['yaw_rate_min'], self.motion_parameters['yaw_rate_max'])
            self.motion_inputs.step_length = self.map(
               - self.gamepad.axis('LEFT-Y'), -1, 1, self.motion_parameters['step_length_min'], self.motion_parameters['step_length_max'])          
            self.motion_inputs.yaw_rate = self.map(
              self.gamepad.axis('RIGHT-X'), -1, 1, self.motion_parameters['yaw_rate_min'], self.motion_parameters['yaw_rate_max'])            
            self.motion_inputs.pos[2] = self.map(
              - self.gamepad.axis('RIGHT-Y'), -1, 1, self.motion_parameters['pos_z_min'], self.motion_parameters['pos_z_max'])

        
        # TEMP FOR INITIAL MODEL SETUP
        self.motion_inputs.orn[0] = 0
        self.motion_inputs.orn[1] = 0
        self.motion_inputs.orn[2] = 0
        
        self.motion_inputs.pos[0] = 0
        self.motion_inputs.pos[1] = 0
        #self.motion_inputs.pos[2] = 0
        
        return copy.deepcopy(self.motion_inputs)
                        
        
    def disconnect(self):          
        self.gamepad.disconnect()    

    ###############################################################################
    # Helpers
    ###############################################################################

    def map(self, n, in_min, in_max, out_min, out_max):
        return (n - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    

###############################################################################
# Main - Run to test class.
###############################################################################
if __name__ == '__main__':
       
    motion_parameters_filepath = "./parameters/motion_parameters.yaml"
    if os.path.exists(motion_parameters_filepath):
        with open(motion_parameters_filepath, 'r') as stream:
            motion_parameters = yaml.safe_load(stream)
    else:
        print(f"[SYSTEM] parameter file not found! {motion_parameters_filepath}")
        exit(1)

    gamepad_interface = GamepadInterface(motion_parameters)
    gamepad_interface.connect_gamepad()
    
    try:  
        while(True):
            motion_inputs = gamepad_interface.get_motion_inputs()
            print(motion_inputs.orn)
            sleep(0.100)

    except KeyboardInterrupt:
        pass

    finally: 
        gamepad_interface.disconnect()