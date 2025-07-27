import copy
import math
import numpy as np
from math import pi, sin, cos
from enum import Enum
from typing import Dict
from typing import Dict, List

from .leg import Leg
from . import kinematics
from . import transformations
from .exceptions import DomainBreach
from system.quadruped.parameters.frame_parameters import FrameParameters
from system.quadruped.parameters.motion_parameters import MotionParameters
from system.quadruped.point import Point


class Quad(object):
    """
    Encapsulates a 12 DOF quadruped.

    The 12 degrees of freedom represent the twelve joint angles.
    Generates inverse kinematics to calculate joint angles.

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
        KINEMATICS = 2
        JOINT = 3

    def __init__(self):
        self.frame_parameters = FrameParameters()

        self.hip_length = self.frame_parameters.hip_length
        self.upper_leg_length = self.frame_parameters.upper_leg_length
        self.lower_leg_length = self.frame_parameters.lower_leg_length
        self.body_width = self.frame_parameters.body_width
        self.body_length = self.frame_parameters.body_length
        self.foot_length = self.frame_parameters.foot_length
        self.foot_width = self.frame_parameters.foot_width

        self.legs: Dict[str, Leg] = {}
    
        z_avg = (MotionParameters().height_translation_min + MotionParameters().height_translation_max) / 2

        # Initialize legs at the neutral position
        self.set_body_pose_by_transform_inputs(
            phi=0,
            theta=0,
            psi=0,
            x=0,
            y=z_avg/2,
            z=0,
        )

    def create_default_global_foot_positions(self):
        """Creates a default global foot positions dict for reference and testing."""
        l = self.body_length
        w = self.body_width
        l1 = self.hip_length
        offset = -0.00  # TEMP: for testing stylistic poses

        global_foot_positions = {}
        global_foot_positions["front_left"] = [l / 2, 0, -w / 2 - l1 - offset]
        global_foot_positions["front_right"] = [l / 2, 0, w / 2 + l1 + offset]
        global_foot_positions["back_left"] = [-l / 2, 0, -w / 2 - l1 - offset]
        global_foot_positions["back_right"] = [-l / 2, 0, w / 2 + l1 + offset]

        return global_foot_positions

    def set_body_pose_by_transform_inputs(self, phi, theta, psi, x, y, z):
        """Set the body translation and orientation angles
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
            ErrorState

        Performs inverse kinematics on joints prior to saving the results into the legs allowing
        to throw exceptions during calculations to prevent domain breaches or undesired poses
        on a physical system.
        """

        try:
            ht_body = np.matmul(transformations.homog_transxyz(x, y, z), transformations.homog_rotxyz(phi, psi, theta))

            #legs: Dict[str, Leg] = {}
            self.legs["front_left"] = Leg(
                0,
                0,
                0,
                self.hip_length,
                self.upper_leg_length,
                self.lower_leg_length,
                kinematics.t_front_left(ht_body, self.body_length, self.body_width),
                leg12=False,
            )
            self.legs["front_right"] = Leg(
                0,
                0,
                0,
                self.hip_length,
                self.upper_leg_length,
                self.lower_leg_length,
                kinematics.t_front_right(ht_body, self.body_length, self.body_width),
                leg12=True,
            )
            self.legs["back_left"] = Leg(
                0,
                0,
                0,
                self.hip_length,
                self.upper_leg_length,
                self.lower_leg_length,
                kinematics.t_back_left(ht_body, self.body_length, self.body_width),
                leg12=False,
            )
            self.legs["back_right"] = Leg(
                0,
                0,
                0,
                self.hip_length,
                self.upper_leg_length,
                self.lower_leg_length,
                kinematics.t_back_right(ht_body, self.body_length, self.body_width),
                leg12=True,
            )

            global_foot_positions = self.create_default_global_foot_positions()

            for key in self.legs.keys():
                x4 = global_foot_positions[key][0]
                y4 = global_foot_positions[key][1]
                z4 = global_foot_positions[key][2]
                self.legs[key].set_foot_position_in_global_coords(x4, y4, z4)

            error_string = self.check_joint_angles(self.legs)
            if error_string != None:
                print(error_string)
                return Quad.ErrorState.JOINT
        
        except DomainBreach as error:
            print(error)
            return Quad.ErrorState.KINEMATICS

        return Quad.ErrorState.NONE
    

    def get_body_coordinates(self) -> dict[str, Point]:
        """
        Return coordinates of each hip as a list of 4 points
        """
         
        return {
            'BR': self.legs["back_right"].get_hip_point(),
            'FR': self.legs["front_right"].get_hip_point(),
            'FL': self.legs["front_left"].get_hip_point(),
            'BL': self.legs["back_left"].get_hip_point(),
        }

    def get_leg_coordinates(self) -> dict[str, list[Point]]:
        """
        Return coordinates of each leg as a dict containing 4 sets of 4 leg points
        """
         
        return {
            'BR': self.legs["back_right"].get_leg_points(),
            'FR': self.legs["front_right"].get_leg_points(),
            'FL': self.legs["front_left"].get_leg_points(),
            'BL': self.legs["back_left"].get_leg_points(),
        }
       

    def set_joint_angles(self, leg_angs):
        """Set the joint angles for all four legs
            Purpose is external wireframe and simulation verification only

        Args:
            leg_angs: Tuple of 4 lists of leg angles. Legs in the order backright, frontright, frontleft, backleft. ANgles in the order q1,q2,q3.
                      An example input:
                        ((rb_q1,rb_q2,rb_q3),
                         (rf_q1,rf_q2,rf_q3),
                         (lf_q1,lf_q2,lf_q3),
                         (lb_q1,lb_q2,lb_q3))

        Returns:
            Nothing
        """
        self.legs["back_right"].set_angles(leg_angs[0][0], leg_angs[0][1], leg_angs[0][2])
        self.legs["front_right"].set_angles(leg_angs[1][0], leg_angs[1][1], leg_angs[1][2])
        self.legs["front_left"].set_angles(leg_angs[2][0], leg_angs[2][1], leg_angs[2][2])
        self.legs["back_left"].set_angles(leg_angs[3][0], leg_angs[3][1], leg_angs[3][2])

    def get_joint_angles(self, units: str):
        """Get the joint angles for all four legs
        Args:
            units: RADIANS for radians, DEGREES for degrees
        Returns:
            joint_angles: dictionary containing four legs and their
            associated angles in the order q1,q2,q3
        """
        if units.upper() == "RADIANS":
            joint_angles = {}
            joint_angles["front_left"] = self.legs["front_left"].get_leg_angles_in_radians()
            joint_angles["front_right"] = self.legs["front_right"].get_leg_angles_in_radians()
            joint_angles["back_left"] = self.legs["back_left"].get_leg_angles_in_radians()
            joint_angles["back_right"] = self.legs["back_right"].get_leg_angles_in_radians()
        elif units.upper() == "DEGREES":
            joint_angles = {}
            joint_angles["front_left"] = self.legs["front_left"].get_leg_angles_in_degrees()
            joint_angles["front_right"] = self.legs["front_right"].get_leg_angles_in_degrees()
            joint_angles["back_left"] = self.legs["back_left"].get_leg_angles_in_degrees()
            joint_angles["back_right"] = self.legs["back_right"].get_leg_angles_in_degrees()

        return joint_angles

    def check_joint_angles(self, legs: Dict[str, Leg]):
        """Checks the bounds of joint angles
        Args:
            Legs dictionary to check
        Returns:
            None: no error
            string: error (string describes the error)
        """

        for key, leg in legs.items():
            angles = leg.get_leg_angles_in_radians()
            abduction = angles["abduction"]
            hip = angles["hip"]
            knee = angles["knee"]
            if abduction < self.frame_parameters.abduction_joint_lower_bounds or abduction > self.frame_parameters.abduction_joint_upper_bounds:
                return f"Leg {key} {'abduction'} joint is out of bounds where angle {math.degrees(abduction):0.2f} is outside of [{math.degrees(self.frame_parameters.abduction_joint_lower_bounds):0.2f}, {math.degrees(self.frame_parameters.abduction_joint_upper_bounds):0.2f}]!"
            if hip < self.frame_parameters.hip_joint_lower_bounds or hip > self.frame_parameters.hip_joint_upper_bounds:
                return f"Leg {key} {'hip'} joint is out of bounds where angle {math.degrees(hip):0.2f} is outside of [{math.degrees(self.frame_parameters.hip_joint_lower_bounds):0.2f}, {math.degrees(self.frame_parameters.hip_joint_upper_bounds):0.2f}]!"
            if knee < self.frame_parameters.knee_joint_lower_bounds or knee > self.frame_parameters.knee_joint_upper_bounds:
                return f"Leg {key} {'knee'} joint is out of bounds where angle {math.degrees(knee):0.2f} is outside of [{math.degrees(self.frame_parameters.knee_joint_lower_bounds):0.2f}, {math.degrees(self.frame_parameters.knee_joint_upper_bounds):0.2f}]!"

    def print_joint_angles(self):
        """Print the joint angles for all four legs"""
        return None
