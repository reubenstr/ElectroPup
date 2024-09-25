#!/usr/bin/env python3

import os
import yaml
import math
import copy
from time import sleep
import numpy as np

#from bezier_gait import BezierGait

# Local source.
from model.body import Body
from GamepadInterface import GamepadInterface
from FrameParameters import FrameParameters
from MotionParameters import MotionParameters

###############################################################################
# Commander
###############################################################################

class Commander():
    def __init__(self): 
   
        self.joint_angles = None

        ###############################################################################
        # Setup dependancies
        ###############################################################################

        motion_parameters_filepath = "./parameters/motion_parameters.yaml"
        frame_parameters_filepath = "./parameters/frame_parameters.yaml"
            
        self.frame_parameters = FrameParameters(frame_parameters_filepath)
        self.motion_parameters = MotionParameters(motion_parameters_filepath)

        self.gamepad_interface = GamepadInterface(self.motion_parameters)
        self.gamepad_interface.connect_gamepad()

        self.body = Body(frame_parameters=self.frame_parameters)

        #self.bezier_gait = BezierGait(dt=0.01)
        #self.kinematics = Kinematics(self.frame_parameters)  

         
    def tick(self):
        #lateral_fraction = self.motion_parameters['lateral_fraction']
        #step_velocity = self.motion_parameters['step_velocity']
        #clearance_height = self.motion_parameters['clearance_height']     
        #penetration_depth = self.motion_parameters['penetration_depth'] 
        #contacts = [0, 0, 0, 0] # TODO        
        # self.bezier_gait.Tswing = self.motion_parameters.swing_period
        # yaw correction TODO 
        # self.T_bf = copy.deepcopy(self.kinematics.WorldToFoot)
        # orn = np.array([0, 0, 0])
        # pos = np.array([0, 0, -0.00])

        #print(f"[ORN] {orn}")
        #print(f"[POS] {pos}") 
        #self.joint_angles = self.kinematics.inverse_kinematics(orn, pos, self.T_bf) 
        #self.joint_angles = self.sm.IK(orn, pos, self.T_bf)

        #height = 0.140
        #foot_width = 0.2605
        #foot_length = 0.338
        #bodytoFeet0 = np.matrix([[ foot_length , -foot_width , -height],
        #                         [foot_length ,  foot_width , -height],
        #                         [-foot_length , -foot_width , -height],
        #                         [-foot_length ,  foot_width , -height]])
        #self.joint_angles = self.rk.solve(orn, pos, bodytoFeet0)

        # ja = [math.degrees(radian) for radian in self.joint_angles]       
        #print(f"[JA][FL] {ja[0]:3.2f}, {ja[1]:3.2f}, {ja[2]:3.2f}")
        #print(f"[JA][FR] {ja[3]:3.2f}, {ja[4]:3.2f}, {ja[5]:3.2f}")  
        #print(f"[JA][BL] {ja[6]:3.2f}, {ja[7]:3.2f}, {ja[8]:3.2f}")  
        #print(f"[JA][BR] {ja[9]:3.2f}, {ja[10]:3.2f}, {ja[11]:3.2f}")    

        
        
        motion_parameters = self.gamepad_interface.get_motion_parameters()
        #motion_parameters.roll = math.radians(30)        
        self.body.set_body_pose_by_transform_inputs(x=motion_parameters.side_translation,y=motion_parameters.height_translation,z=motion_parameters.forward_translation, phi=motion_parameters.roll, theta=motion_parameters.pitch, psi=motion_parameters.yaw)
        
        self.joint_angles = self.body.get_joint_angles()
  

        
        """    # Manual stylized pose to verify model and joint angles correct correlation.
        # FL
        self.joint_angles[0] = math.radians(-10)
        self.joint_angles[1] = math.radians(-45)
        self.joint_angles[2] = math.radians(-90)
        #FR
        self.joint_angles[3] = math.radians(10)
        self.joint_angles[4] = math.radians(45)
        self.joint_angles[5] = math.radians(90)
        #BL
        self.joint_angles[6] = math.radians(10)
        self.joint_angles[7] = math.radians(-45)
        self.joint_angles[8] = math.radians(-90)
        #BR
        self.joint_angles[9] = math.radians(-10)
        self.joint_angles[10] = math.radians(45)
        self.joint_angles[11] = math.radians(90)  """

        """ # FL
        self.joint_angles[0] = self.joint_angles[0]
        self.joint_angles[1] = self.joint_angles[1]
        self.joint_angles[2] = self.joint_angles[2] - math.radians(180)
        #FR
        self.joint_angles[3] = self.joint_angles[3]
        self.joint_angles[4] = -self.joint_angles[4] 
        self.joint_angles[5] = -self.joint_angles[5] - math.radians(180)
        #BL
        self.joint_angles[6] = self.joint_angles[6]
        self.joint_angles[7] = self.joint_angles[7]  
        self.joint_angles[8] = self.joint_angles[8] - math.radians(180)
        #BR
        self.joint_angles[9] = self.joint_angles[9]
        self.joint_angles[10] = -self.joint_angles[10] 
        self.joint_angles[11] = -self.joint_angles[11] - math.radians(180)  """ 
                          
        # TODO: apply angles to motors

    def get_joint_angles(self):
        return self.joint_angles
    
    def shutdown(self):
        self.gamepad_interface.disconnect()
        
    
###############################################################################
# Main - Run to test class
###############################################################################
if __name__ == '__main__':

    np.set_printoptions(precision=3) 

    commander = Commander()

    try:    
        while(True):        
            commander.tick()
            joint_angles = commander.get_joint_angles()

            for key, value in joint_angles.items():
                formatted_value = [f"{math.degrees(num):.2f}" for num in value]
                print(f"[{key}] {formatted_value}")
       
            sleep(0.10)

    finally:
        commander.shutdown()

