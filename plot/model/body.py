
import matplotlib.pyplot as plt
import numpy as np
from math import pi, sin, cos

from .leg import Leg
from . import kinematics
from . import transformations
from FrameParameters import FrameParameters

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

        rightback_leg_angles: length 3 list of joint angles. Order: hip, leg, knee
        rightfront_leg_angles: length 3 list of joint angles. Order: hip, leg, knee
        leftfront_leg_angles: length 3 list of joint angles. Order: hip, leg, knee
        leftback_leg_angles: length 3 list of joint angles. Order: hip, leg, knee

        leg_rightback
        leg_rightfront
        leg_leftfront
        leg_leftback
        
    """
    def __init__(self, frame_parameters: FrameParameters):   
        '''Constructor'''

        self.hip_length = frame_parameters.hip_length
        self.upper_leg_length = frame_parameters.upper_leg_length
        self.lower_leg_length = frame_parameters.lower_leg_length
        self.body_width = frame_parameters.body_width
        self.body_length = frame_parameters.body_length

        init_height = (self.upper_leg_length + self.lower_leg_length) / 2.0

        self.x = 0
        self.y = init_height
        self.z = 0        
        self.phi = 0
        self.theta = 0
        self.psi = 0   

        # Initialize Body Pose
        # Convention for this class is to initialize the body pose at a x,y,z position, with a phi,theta,psi orientation
        # To achieve this pose, need to apply a homogeneous translation first, then a homgeneous rotation
        # If done the other way around, a coordinate system will be rotate first, then translated along the rotated coordinate system
        # self.ht_body = transformations.homog_transxyz(self.x,self.y,self.z) @ transformations.homog_rotxyz(self.phi,self.psi,self.theta)
        self.ht_body = np.matmul(transformations.homog_transxyz(self.x,self.y,self.z), transformations.homog_rotxyz(self.phi,self.psi,self.theta))
        
        # Intialize all leg angles to 0, 30, 30 degrees
        self.rb_leg_angles   = [0,-30*d2r,60*d2r]
        self.rf_leg_angles   = [0,-30*d2r,60*d2r]
        self.lf_leg_angles   = [0,30*d2r,-60*d2r]
        self.lb_leg_angles   = [0,30*d2r,-60*d2r]

        # Create a dictionary to hold the legs object.
        # First initialize to empty dict with feet directly below joints.
        self.legs = {}

        self.legs['leg_rightback'] =     Leg(self.rb_leg_angles[0],self.rb_leg_angles[1],self.rb_leg_angles[2],
                                                     self.hip_length,self.upper_leg_length,self.lower_leg_length,
                                                     kinematics.t_rightback(self.ht_body,self.body_length,self.body_width),leg12=True) 
        
        self.legs['leg_rightfront'] =   Leg(self.rf_leg_angles[0],self.rf_leg_angles[1],self.rf_leg_angles[2],
                                                     self.hip_length,self.upper_leg_length,self.lower_leg_length,
                                                     kinematics.t_rightfront(self.ht_body,self.body_length,self.body_width),leg12=True)
                                                  
        self.legs['leg_leftfront'] =    Leg(self.lf_leg_angles[0],self.lf_leg_angles[1],self.lf_leg_angles[2],
                                                     self.hip_length,self.upper_leg_length,self.lower_leg_length,
                                                     kinematics.t_leftfront(self.ht_body,self.body_length,self.body_width),leg12=False)

        self.legs['leg_leftback'] =     Leg(self.lb_leg_angles[0],self.lb_leg_angles[1],self.lb_leg_angles[2],
                                                     self.hip_length,self.upper_leg_length,self.lower_leg_length,
                                                     kinematics.t_leftback(self.ht_body,self.body_length,self.body_width),leg12=False) 

    def get_leg_coordinates(self):
        '''Return coordinates of each leg as a tuple of 4 sets of 4 leg points'''
        
        return (self.legs['leg_rightback'].get_leg_points(),
                self.legs['leg_rightfront'].get_leg_points(),
                self.legs['leg_leftfront'].get_leg_points(),
                self.legs['leg_leftback'].get_leg_points())

    def set_leg_angles(self,leg_angs):
        ''' Set the leg angles for all four legs

        Args:
            leg_angs: Tuple of 4 lists of leg angles. Legs in the order rightback
                      rightfront, leftfront, leftback. ANgles in the order q1,q2,q3.
                      An example input:
                        ((rb_q1,rb_q2,rb_q3),
                         (rf_q1,rf_q2,rf_q3),
                         (lf_q1,lf_q2,lf_q3),
                         (lb_q1,lb_q2,lb_q3))

        Returns:
            Nothing
        '''
        self.legs['leg_rightback'].set_angles(leg_angs[0][0],leg_angs[0][1],leg_angs[0][2])
        self.legs['leg_rightfront'].set_angles(leg_angs[1][0],leg_angs[1][1],leg_angs[1][2])
        self.legs['leg_leftfront'].set_angles(leg_angs[2][0],leg_angs[2][1],leg_angs[2][2])
        self.legs['leg_leftback'].set_angles(leg_angs[3][0],leg_angs[3][1],leg_angs[3][2])            


    def set_absolute_foot_coordinates(self,foot_coords):
        '''Set foot coordinates to a set inputted in the global coordinate frame and compute 
        and set the joint angles to achieve them using inverse kinematics
        
        Args:
            foot_coords: A 4x3 numpy matrix of desired (x4,y4,z4) positions for the end point (point 4) of each of
                    the four legs. I.e., the foot.
                    Leg order: rigthback, rightfront, leftfront, leftback. Example input:
                        np.array( [ [x4_rb,y4_rb,z4_rb],
                                    [x4_rf,y4_rf,z4_rf],
                                    [x4_lf,y4_lf,z4_lf],
                                    [x4_lb,y4_lb,z4_lb] ])
        Returns:
            Nothing
        '''

        # For each leg, call its method to set foot position in global coordinate frame
        
        foot_coords_dict = {'leg_rightback':foot_coords[0],
                            'leg_rightfront':foot_coords[1],
                            'leg_leftfront':foot_coords[2],
                            'leg_leftback':foot_coords[3]}
        
        for leg_name in self.legs:
            x4 = foot_coords_dict[leg_name][0]
            y4 = foot_coords_dict[leg_name][1]
            z4 = foot_coords_dict[leg_name][2]
            self.legs[leg_name].set_foot_position_in_global_coords(x4,y4,z4)

    def set_absolute_body_pose(self, ht_body):
        '''Set absolute pose of body, while holding foot positions in place'''
        
        # Get current foot position of each leg in global coordinate system
        # These are 1x3 numpy arrays
        foot_coords = {}
        for leg_name in self.legs:
            foot_coords[leg_name] = self.legs[leg_name].get_foot_position_in_global_coords()

        # Set body pose
        self.ht_body = ht_body

        # Update each leg's homogeneous transformation 
        self.legs['leg_rightback'].set_homog_transf(kinematics.t_rightback(self.ht_body,self.body_length,self.body_width))
        self.legs['leg_rightfront'].set_homog_transf(kinematics.t_rightfront(self.ht_body,self.body_length,self.body_width))
        self.legs['leg_leftfront'].set_homog_transf(kinematics.t_leftfront(self.ht_body,self.body_length,self.body_width))
        self.legs['leg_leftback'].set_homog_transf(kinematics.t_leftback(self.ht_body,self.body_length,self.body_width))

        # Prep foot coordinates to call method to set absolute foot coordinates
        foot_coords_matrix = np.block([ [foot_coords['leg_rightback']],
                                        [foot_coords['leg_rightfront']],
                                        [foot_coords['leg_leftfront']],
                                        [foot_coords['leg_leftback']]  ])

        print(foot_coords_matrix)
        self.set_absolute_foot_coordinates(foot_coords_matrix)


    def set_body_transform_inputs(self,x,y,z,phi,theta,psi):
        '''Set the body translation and orientation angles

        Args:
            x: translation along the x axis in meters
            y: translation along the y axis in meters
            z: translation along the z axis in meters
            phi: roll angle in radians
            theta: pitch angle in radians
            psi: yaw angle in radians
        Returns:
            Nothing
        '''
        ht_body = transformations.homog_transform(phi, psi, theta, x,y,z)
        self.set_absolute_body_pose(ht_body)

    
    def set_body_angles(self,phi=0,theta=0,psi=0):
        '''Set a body angles without translation of the body

        Args:
            phi: roll angle in radians
            theta: pitch angle in radians
            psi: yaw angle in radians
        Returns:
            Nothing
        '''
        # Create a xyz rotation matrix
        r_xyz = transformations.rotxyz(phi,psi,theta)

        # Get current body pose, and replace rotation part with r_xyz
        ht_body = self.ht_body

        ht_body[0:3,0:3] = r_xyz

        # Call method to set absolute body pose
        self.set_absolute_body_pose(ht_body)

    def get_leg_angles(self):
        ''' Get the leg angles for all four legs
        Args:
            None
        Returns:
            leg_angs: Tuple of 4 of the leg angles. Legs in the order rightback
                      rightfront, leftfront, leftback. Angles in the order q1,q2,q3.
                      An example output:
                        ((rb_q1,rb_q2,rb_q3),
                         (rf_q1,rf_q2,rf_q3),
                         (lf_q1,lf_q2,lf_q3),
                         (lb_q1,lb_q2,lb_q3))
        '''
        return (    self.legs['leg_rightback'].get_leg_angles(),
                    self.legs['leg_rightfront'].get_leg_angles(),
                    self.legs['leg_leftfront'].get_leg_angles(),
                    self.legs['leg_leftback'].get_leg_angles()     )


    def print_leg_angles(self):
        ''' Print the joint angles for alll four legs'''
        return None