#!/usr/bin/env python3

import os
import yaml
import math
from time import sleep

from kinematics import Kinematics
from bezier_gait import BezierGait
from GamepadInterface import GamepadInterface

###############################################################################
# Commander
###############################################################################

class Commander():
    def __init__(self): 

        self.load_parameters()
           
        self.bezier_gait = BezierGait(dt=0.01)
        self.kinematics = Kinematics(self.frame_parameters)  

        self.gamepad_interface = GamepadInterface(self.motion_parameters)
        self.gamepad_interface.connect_gamepad()

        self.joint_angles = None

    def load_parameters(self):

        motion_parameters_filepath = "./parameters/motion_parameters.yaml"
        frame_parameters_filepath = "./parameters/frame_parameters.yaml"
        linked_leg_parameters_filepath = "./parameters/linked_leg_parameters.yaml"
           
        if os.path.exists(motion_parameters_filepath):
            with open(motion_parameters_filepath, 'r') as stream:
                self.motion_parameters = yaml.safe_load(stream)
        else:
            print(f"[Commander] parameter file not found! {motion_parameters_filepath}")

        if os.path.exists(frame_parameters_filepath):
            with open(frame_parameters_filepath, 'r') as stream:
                self.frame_parameters = yaml.safe_load(stream)
        else:
            print(f"[Commander] parameter file not found! {frame_parameters_filepath}")

    def tick(self): 

        motion_inputs = self.gamepad_interface.get_motion_inputs()
        
        # motion_inputs.print()
       
        pos = motion_inputs.pos
        orn = motion_inputs.orn
        step_length = motion_inputs.step_length        
        yaw_rate = motion_inputs.yaw_rate
    
        lateral_fraction = self.motion_parameters['lateral_fraction']
        step_velocity = self.motion_parameters['step_velocity']
        clearance_height = self.motion_parameters['clearance_height']     
        penetration_depth = self.motion_parameters['penetration_depth'] 

        contacts = [0, 0, 0, 0] # TODO
        
        # self.bezier_gait.Tswing = self.motion_parameters.swing_period
        # yaw correction TODO  

        # Get foot positions.       
        self.T_bf = self.bezier_gait.GenerateTrajectory(
            step_length, lateral_fraction, yaw_rate, step_velocity, self.kinematics.WorldToFoot, clearance_height, penetration_depth, contacts)

        print(self.T_bf)

        self.joint_angles = self.kinematics.inverse_kinematics(orn, pos, self.T_bf)              
       
        #joint_angles_linked_leg = self.kinematics.get_joint_angles_linked_legs(joint_angles)          

        # TODO: apply angles to motors

    def get_joint_angles(self):
        return self.joint_angles
    
    def shutdown(self):
        self.gamepad_interface.disconnect()
        
    
###############################################################################
# Main - Run to test class.
###############################################################################
if __name__ == '__main__':

    # TEMP AREA FOR PARAMS
    tick_rate_seconds = 0.010

    commander = Commander()

    try:
    
        while(True):        
            commander.tick()
            joint_angles = commander.get_joint_angles()

            joint_angles = [math.degrees(radian) for radian in joint_angles]
            joint_angles = [f"{num:.2f}" for num in joint_angles]

            print(f"{joint_angles[:3]}")

            sleep(tick_rate_seconds)

    finally:
        commander.shutdown()

