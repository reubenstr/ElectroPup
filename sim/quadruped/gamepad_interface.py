#!/usr/bin/env python3

"""
    Converts gamepad inputs into motion parameters ready to be consumed by kinematics.

    Code assumes using a PS4 controller by default.
"""

import time
import copy
from time import sleep

from . import gamepad
from .parameters.motion_parameters import MotionParameters

class GamepadInterface:
    def __init__(self, motion_parameters: MotionParameters):
        self.motion_parameters = motion_parameters
      
    def connect_gamepad(self):
        # Find the ID of the connected joystick (gamepad): "ls /dev/input/ | grep js"
        joystick_id = 0  
        
        max_retries = 3
        retry = 0
        print(f"[GAMEPAD] attempting to connect to joystick with ID {joystick_id}...")
        while not gamepad.available(joystick_id):
            print(f"[GAMEPAD] joystick not detected on ID {joystick_id}!")
            retry += 1
            if retry  > max_retries:
                return False
            time.sleep(1.0)
            
        print(f"[GAMEPAD] joystick connected on ID {joystick_id}")
        self.gamepad = gamepad.PS4(joystick_id)              
        self.gamepad.startBackgroundUpdates()
        return True

    def get_motion_parameters(self):
            
        # BUTTONS:        
        if self.gamepad.isPressed("TRIANGLE") == True and self.mode_toggle_button_release_flag == True:
            self.mode_toggle_button_release_flag = False
            if self.motion_parameters.motion_state == MotionParameters.MotionState.MOTION:
                self.motion_parameters.motion_state = MotionParameters.MotionState.POSE
            elif self.motion_parameters.motion_state == MotionParameters.MotionState.POSE:
                self.motion_parameters.motion_state = MotionParameters.MotionState.MOTION
        elif self.gamepad.isPressed("TRIANGLE") == False:
            self.mode_toggle_button_release_flag = True
                  
        # AXES:    
        # Joystick at up position generates negative values.
        # Joystick at down position generates positive values.
        # Some inputs reorientates some joysticks to match desired functionality.            
        if self.motion_parameters.motion_state == MotionParameters.MotionState.POSE:                      
            self.motion_parameters.roll = self.map(
                self.gamepad.axis('LEFT-X'), -1, 1, self.motion_parameters.roll_min, self.motion_parameters.roll_max)
            self.motion_parameters.pitch = self.map(
             - self.gamepad.axis('LEFT-Y'), -1, 1, self.motion_parameters.pitch_min, self.motion_parameters.pitch_max)
            self.motion_parameters.yaw = self.map(
                self.gamepad.axis('RIGHT-X'), -1, 1, self.motion_parameters.yaw_min, self.motion_parameters.yaw_max)
            self.motion_parameters.height_translation = self.map(
            - self.gamepad.axis('RIGHT-Y'), -1, 1, self.motion_parameters.height_translation_min, self.motion_parameters.height_translation_max)
                      
        elif self.motion_parameters.motion_state == MotionParameters.MotionState.MOTION:
            self.motion_parameters.yaw_rate = self.map(
                self.gamepad.axis('LEFT-X'), -1, 1, self.motion_parameters.yaw_rate_min, self.motion_parameters.yaw_rate_max)
            self.motion_parameters.step_length = self.map(
             - self.gamepad.axis('LEFT-Y'), -1, 1, self.motion_parameters.step_length_min, self.motion_parameters.step_length_max)          
            self.motion_parameters.yaw_rate = self.map(
              self.gamepad.axis('RIGHT-X'), -1, 1, self.motion_parameters.yaw_rate_min, self.motion_parameters.yaw_rate_max)            
            self.motion_parameters.height_translation = self.map(
            - self.gamepad.axis('RIGHT-Y'), -1, 1, self.motion_parameters.height_translation_min, self.motion_parameters.height_translation_max)
                   
        return copy.deepcopy(self.motion_parameters)

    def disconnect(self):          
        self.gamepad.disconnect()    
  
    def map(self, n, in_min, in_max, out_min, out_max):
        return (n - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    

###############################################################################
# Main - Run to test class.
###############################################################################
if __name__ == '__main__':
       
    motion_parameters_filepath = "./parameters/motion_parameters.yaml"
    motion_parameters = MotionParameters(motion_parameters_filepath)
    if motion_parameters.is_error():
         print(f"[SYSTEM] parameter file not found! {motion_parameters_filepath}")
         exit(1)

    gamepad_interface = GamepadInterface(motion_parameters)
    gamepad_interface.connect_gamepad()
    
    try:  
        while(True):
            motion_parameters = gamepad_interface.get_motion_parameters()
            motion_parameters.print()
            sleep(0.100)

    except KeyboardInterrupt:
        pass

    finally: 
        gamepad_interface.disconnect()