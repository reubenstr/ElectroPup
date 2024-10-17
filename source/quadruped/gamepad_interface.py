#!/usr/bin/env python3

"""
    Converts gamepad inputs into motion parameters ready to be consumed by kinematics.

    Code assumes using a PS4 controller by default.
"""

import copy
from time import sleep
from typing import Callable, Optional

from . gamepad import PS4
from . parameters.motion_parameters import MotionParameters, KineticState, ControllerEvent

class GamepadInterface:
    def __init__(self, motion_parameters: MotionParameters):
        self.motion_parameters = motion_parameters
                
        self.controller_event_callback: Optional[Callable[[ControllerEvent], None]] = None   
        
        self.triangle_button_release_flag = True
        self.r3_button_release_flag = True
        self.l3_button_release_flag = True
        
    def register_controller_event_callback(self, callback: Callable[[ControllerEvent], None]):
        self.controller_event_callback = callback
        
    def trigger_controller_event(self, event: ControllerEvent):
        if self.controller_event_callback:
            self.controller_event_callback(event)
              
    def connect_gamepad(self):
        # Find the ID of the connected joystick (gamepad): "ls /dev/input/ | grep js"
        joystick_number = 0                   
        self.gamepad = PS4(joystick_number)              
        self.gamepad.startBackgroundUpdates()
        return True
    
    def get_motion_parameters(self, motion_state: KineticState):
            
        # BUTTONS:        
        if self.gamepad.isPressed("TRIANGLE") == True and self.triangle_button_release_flag == True:
            self.triangle_button_release_flag = False            
            self.trigger_controller_event(ControllerEvent.KINETIC_STATE_TOGGLE)            
        elif self.gamepad.isPressed("TRIANGLE") == False:
            self.triangle_button_release_flag = True
            
        if self.gamepad.isPressed("L3") == True and self.l3_button_release_flag == True and self.gamepad.isPressed("R3") == True and self.r3_button_release_flag == True:             
            self.r3_button_release_flag = False  
            self.l3_button_release_flag = False 
            self.trigger_controller_event(ControllerEvent.MOTOR_POWER_TOGGLE)             
        elif self.gamepad.isPressed("L3")  and self.gamepad.isPressed("R3")== False:
            self.r3_button_release_flag = True  
            self.l3_button_release_flag = True  
            
            
                  
        # AXES:    
        # Joystick at up position generates negative values.
        # Joystick at down position generates positive values.
        # Some inputs reorientates some joysticks to match desired functionality.            
        if motion_state == KineticState.POSE:                      
            self.motion_parameters.roll = self.map(
                self.gamepad.axis('LEFT-X'), -1, 1, self.motion_parameters.roll_min, self.motion_parameters.roll_max)
            self.motion_parameters.pitch = self.map(
             - self.gamepad.axis('LEFT-Y'), -1, 1, self.motion_parameters.pitch_min, self.motion_parameters.pitch_max)
            self.motion_parameters.yaw = self.map(
                self.gamepad.axis('RIGHT-X'), -1, 1, self.motion_parameters.yaw_min, self.motion_parameters.yaw_max)
            self.motion_parameters.height_translation = self.map(
            - self.gamepad.axis('RIGHT-Y'), -1, 1, self.motion_parameters.height_translation_min, self.motion_parameters.height_translation_max)
                      
        elif motion_state == KineticState.MOTION:
            self.motion_parameters.yaw_rate = self.map(
                self.gamepad.axis('LEFT-X'), -1, 1, self.motion_parameters.yaw_rate_min, self.motion_parameters.yaw_rate_max)
            self.motion_parameters.step_length = self.map(
             - self.gamepad.axis('LEFT-Y'), -1, 1, self.motion_parameters.step_length_min, self.motion_parameters.step_length_max)          
            self.motion_parameters.yaw_rate = self.map(
              self.gamepad.axis('RIGHT-X'), -1, 1, self.motion_parameters.yaw_rate_min, self.motion_parameters.yaw_rate_max)            
            self.motion_parameters.height_translation = self.map(
            - self.gamepad.axis('RIGHT-Y'), -1, 1, self.motion_parameters.height_translation_min, self.motion_parameters.height_translation_max)
                   
        return copy.deepcopy(self.motion_parameters)

    def is_connected(self):          
        return self.gamepad.isConnected()

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