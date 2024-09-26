

import copy
import math
import numpy as np
from math import pi, sin, cos
from enum import Enum

from .leg import Leg
from . import kinematics
from . import transformations
from FrameParameters import FrameParameters
from .exceptions import DomainBreach

d2r = pi/180
r2d = 180/pi

class Body(object):
    """
    Encapsulates an 12 DOF quadruped stick figure  

    The 12 degrees of freedom represent the twelve joint angles. 
    Contains inverse kinematic capabilities
    
    Attributes:
        hip_length: Length of the hip joint
        upper_leg_length: length of the upper leg link
        lower_leg_length: length of the lower leg length
        body_width: width of the robot body
        body_height: length of the robot body

        x: x position of body center
        y: y position of body center
        z: z position of body center

        phi: roll angle in radians of body
        theta: pitch angle in radians of body
        psi: yaw angle in radians of body

        ht_body: homogeneous transformation matrix of the body

        back_right_leg_angles: length 3 list of joint angles. Order: hip, leg, knee
        front_right_leg_angles: length 3 list of joint angles. Order: hip, leg, knee
        front_left_leg_angles: length 3 list of joint angles. Order: hip, leg, knee
        back_left_leg_angles: length 3 list of joint angles. Order: hip, leg, knee
    """

    
    class ErrorState(Enum):
        NONE = 1
        IK = 2
        JOINT = 3

    def __init__(self, frame_parameters: FrameParameters):   
        '''Constructor'''

        self.frame_parameters = frame_parameters

        self.hip_length = frame_parameters.hip_length
        self.upper_leg_length = frame_parameters.upper_leg_length
        self.lower_leg_length = frame_parameters.lower_leg_length
        self.body_width = frame_parameters.body_width
        self.body_length = frame_parameters.body_length
        self.foot_length = frame_parameters.foot_length
        self.foot_width = frame_parameters.foot_width
    
        self.legs = {}
        self.legs['back_right'] = None        
        self.legs['front_right'] = None                                                  
        self.legs['front_left'] = None
        self.legs['back_left'] = None

    def create_default_global_foot_positions(self):
        ''' Creates a default global foot positions dict for reference and testing.      
        
        '''
        l = self.body_length
        w = self.body_width
        l1 = self.hip_length
        offset = -0.00      
        
        global_foot_positions = {}
        global_foot_positions['back_right'] = [-l/2,   0,  w/2 + l1 + offset]
        global_foot_positions['front_right'] = [ l/2 ,  0,  w/2 + l1+ offset]
        global_foot_positions['front_left'] = [ l/2 ,  0, -w/2 - l1- offset]
        global_foot_positions['back_left'] = [-l/2 ,  0, -w/2 - l1- offset]

        return global_foot_positions

        
    def set_body_pose_by_transform_inputs(self,phi,theta,psi,x,y,z):
        ''' Set the body translation and orientation angles
            Perform full inverse kinematics
            Check for domain breaches and joint boundries errors

        Args:
            x: translation along the x axis in meters
            y: translation along the y axis in meters
            z: translation along the z axis in meters
            phi: roll angle in radians
            theta: pitch angle in radians
            psi: yaw angle in radians
        Returns:
            Nothing

        Performs inverse kinematics on joints prior to saving the results into the legs allowing
        to throw exceptions during calculations to prevent domain breaches or undesired poses
        on a physical system.
        '''
     
        try:
            ht_body = transformations.homog_transform(phi, psi, theta, x, y, z)
                        
            legs = {}
            legs['back_right'] = Leg(0, 0, 0, self.hip_length,self.upper_leg_length,self.lower_leg_length, kinematics.t_back_right(ht_body,self.body_length,self.body_width),leg12=True) 
            legs['front_right'] = Leg(0, 0, 0, self.hip_length,self.upper_leg_length,self.lower_leg_length, kinematics.t_front_right(ht_body,self.body_length,self.body_width),leg12=True)
            legs['front_left'] = Leg(0, 0, 0, self.hip_length,self.upper_leg_length,self.lower_leg_length, kinematics.t_front_left(ht_body,self.body_length,self.body_width),leg12=False)
            legs['back_left'] = Leg(0, 0, 0, self.hip_length,self.upper_leg_length,self.lower_leg_length, kinematics.t_back_left(ht_body,self.body_length,self.body_width),leg12=False)
            
            global_foot_positions = self.create_default_global_foot_positions()
                          
            for key in legs.keys():
                x4 = global_foot_positions[key][0]
                y4 = global_foot_positions[key][1]
                z4 = global_foot_positions[key][2]
                legs[key].set_foot_position_in_global_coords(x4,y4,z4)

            error_string = self.check_joint_angles(legs)
            if error_string != None:
                print(error_string)
                return Body.ErrorState.JOINT

                
            for key in self.legs.keys():
                self.legs[key] = legs[key]

        except DomainBreach as error:
            print(error) 
            return Body.ErrorState.IK      
      
        return Body.ErrorState.NONE
        
        
    def get_leg_coordinates(self):
        '''Return coordinates of each leg as a tuple of 4 sets of 4 leg points'''
        
        return (self.legs['back_right'].get_leg_points(),
                self.legs['front_right'].get_leg_points(),
                self.legs['front_left'].get_leg_points(),
                self.legs['back_left'].get_leg_points())   
         

    def set_joint_angles(self,leg_angs):
        ''' Set the joint angles for all four legs
            Purpose is model verification

        Args:
            leg_angs: Tuple of 4 lists of leg angles. Legs in the order backright, frontright, frontleft, backleft. ANgles in the order q1,q2,q3.
                      An example input:
                        ((rb_q1,rb_q2,rb_q3),
                         (rf_q1,rf_q2,rf_q3),
                         (lf_q1,lf_q2,lf_q3),
                         (lb_q1,lb_q2,lb_q3))

        Returns:
            Nothing
        '''
        self.legs['back_right'].set_angles(leg_angs[0][0],leg_angs[0][1],leg_angs[0][2])
        self.legs['front_right'].set_angles(leg_angs[1][0],leg_angs[1][1],leg_angs[1][2])
        self.legs['front_left'].set_angles(leg_angs[2][0],leg_angs[2][1],leg_angs[2][2])
        self.legs['back_left'].set_angles(leg_angs[3][0],leg_angs[3][1],leg_angs[3][2])    

    
    def get_joint_angles(self):
        ''' Get the joint angles for all four legs
        Args:
            None
        Returns:
            joint_angles: dictionary containing four legs and their 
            associated angles in the order q1,q2,q3  
        '''

        joint_angles = {}
        joint_angles['front_left'] = self.legs['front_left'].get_leg_angles()
        joint_angles['front_right'] = self.legs['front_right'].get_leg_angles()
        joint_angles['back_left'] = self.legs['back_left'].get_leg_angles()
        joint_angles['back_right'] = self.legs['back_right'].get_leg_angles()
        
        return joint_angles
    
    
    def check_joint_angles(self, legs):
        ''' Checks the bounds of joint angles        
        Args:
            Legs dictionary to check
        Returns:
            None: no error
            string: error (string describes the error)
        '''

        for key, leg in legs.items():
            abduction, hip, knee = leg.get_leg_angles()   
            if abduction < self.frame_parameters.abduction_joint_lower_bounds or abduction > self.frame_parameters.abduction_joint_upper_bounds:
                return f"Leg {key} {'abduction'} joint is out of bounds where angle {math.degrees(abduction):0.2f} is outside of [{math.degrees(self.frame_parameters.abduction_joint_lower_bounds):0.2f}, {math.degrees(self.frame_parameters.abduction_joint_upper_bounds):0.2f}]!"
            if hip < self.frame_parameters.hip_joint_lower_bounds or hip > self.frame_parameters.hip_joint_upper_bounds:
                return f"Leg {key} {'hip'} joint is out of bounds where angle {math.degrees(hip):0.2f} is outside of [{math.degrees(self.frame_parameters.hip_joint_lower_bounds):0.2f}, {math.degrees(self.frame_parameters.hip_joint_upper_bounds):0.2f}]!"
            if knee < self.frame_parameters.knee_joint_lower_bounds or knee > self.frame_parameters.knee_joint_upper_bounds:
                return f"Leg {key} {'knee'} joint is out of bounds where angle {math.degrees(knee):0.2f} is outside of [{math.degrees(self.frame_parameters.knee_joint_lower_bounds):0.2f}, {math.degrees(self.frame_parameters.knee_joint_upper_bounds):0.2f}]!"


    def print_joint_angles(self):
        ''' Print the joint angles for all four legs'''
        return None
    
    
    def get_error_state(self):     
        return self.error_state