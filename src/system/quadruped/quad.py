import math
import numpy as np
from math import pi, sin, cos, radians, degrees
from enum import Enum
from typing import Dict
from typing import Dict, List

from .leg import Leg
from . import kinematics
from . import transformations
from . exceptions import DomainBreach
from . interfaces import LegName, AngleUnits, QuadErrorState
from quadruped.parameters.frame_parameters import FrameParameters
from quadruped.parameters.motion_parameters import MotionParameters
from quadruped.parameters.ik_parameters import IKParameters
from quadruped.point import Point



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
 

    def __init__(self, supress_prints: bool = False):
        self.frame_parameters = FrameParameters()
        self.hip_length = self.frame_parameters.hip_length
        self.upper_leg_length = self.frame_parameters.upper_leg_length
        self.lower_leg_length = self.frame_parameters.lower_leg_length
        self.body_width = self.frame_parameters.body_width
        self.body_length = self.frame_parameters.body_length
        self.foot_length = self.frame_parameters.foot_length
        self.foot_width = self.frame_parameters.foot_width

        self.tag = 'Quad'

        self.joint_angle_error: bool = False
        self.ik_error: bool = False

        self.legs: Dict[LegName, Leg] = {}

        # Initialize legs at the neutral position
        ik_parameters = IKParameters()        
        base_foot_positions = self.get_base_foot_points()
        self.set_body_pose_by_transform_inputs(ik_parameters, base_foot_positions)

    ###############################################################################
    # Methods
    ###############################################################################

    def get_base_foot_point(self, name: LegName) -> Point:
        """ """
        base_foot_positions = self.get_base_foot_points()
        if name in base_foot_positions:
            return base_foot_positions[name]

    def get_base_foot_points(self) -> Dict[LegName, Point]:
        """
        Creates default foot positions in Z up coord system
        """
        l = self.body_length
        w = self.body_width
        l1 = self.hip_length
        offset = 0

        global_foot_positions = {}
        global_foot_positions[LegName.FR] = Point(l / 2, -w / 2 - l1 - offset, 0)
        global_foot_positions[LegName.FL] = Point(l / 2, w / 2 + l1 + offset, 0)
        global_foot_positions[LegName.BR] = Point(-l / 2, -w / 2 - l1 - offset, 0)
        global_foot_positions[LegName.BL] = Point(-l / 2, w / 2 + l1 + offset, 0)

        return global_foot_positions

    def set_body_pose_by_transform_inputs(self, ik_parameters: IKParameters, foot_positions: Dict[LegName, Point]) -> QuadErrorState:
        """
        Set the body translation and orientation angles
        Perform full inverse kinematics
        Check for domain breaches and joint boundries errors

        Args:
            ik_parameters containing rotation and translation values
        Returns:
            ErrorState

        Performs inverse kinematics on joints prior to saving the results into the legs allowing
        to throw exceptions during calculations to prevent domain breaches or undesired poses
        on a physical system.
        """

        phi = radians(ik_parameters.roll)
        theta = radians(ik_parameters.pitch)
        psi = radians(ik_parameters.yaw)
        x = ik_parameters.forward_translation
        y = ik_parameters.height_translation
        z = ik_parameters.side_translation

        try:
            ht_body = np.matmul(transformations.homog_transxyz(x, y, z), transformations.homog_rotxyz(phi, psi, theta))

            self.legs[LegName.FR] = Leg(
                0,
                0,
                0,
                self.hip_length,
                self.upper_leg_length,
                self.lower_leg_length,
                kinematics.t_front_left(ht_body, self.body_length, self.body_width),
                foot_positions[LegName.FR],
                leg12=False,
            )
            self.legs[LegName.FL] = Leg(
                0,
                0,
                0,
                self.hip_length,
                self.upper_leg_length,
                self.lower_leg_length,
                kinematics.t_front_right(ht_body, self.body_length, self.body_width),
                foot_positions[LegName.FL],
                leg12=True,
            )
            self.legs[LegName.BR] = Leg(
                0,
                0,
                0,
                self.hip_length,
                self.upper_leg_length,
                self.lower_leg_length,
                kinematics.t_back_left(ht_body, self.body_length, self.body_width),
                foot_positions[LegName.BR],
                leg12=False,
            )
            self.legs[LegName.BL] = Leg(
                0,
                0,
                0,
                self.hip_length,
                self.upper_leg_length,
                self.lower_leg_length,
                kinematics.t_back_right(ht_body, self.body_length, self.body_width),
                foot_positions[LegName.BL],
                leg12=True,
            )

            error_string = self.check_joint_angles()
            if error_string != None:
                print(error_string)
                self.joint_angle_error = True
                return
            
            error_string = self.check_ground_penetration()
            if error_string != None:
                print(error_string)
                self.joint_angle_error = True
                return             

        except DomainBreach as error:
            print(error)
            self.ik_error = True
            return

        self.joint_angle_error = False
        self.ik_error = False
        

    def get_body_coordinates(self) -> dict[LegName, Point]:
        """
        Return coordinates of each hip as a list of 4 points
        """

        return {
            LegName.BL: self.legs[LegName.BL].get_hip_point(),
            LegName.FL: self.legs[LegName.FL].get_hip_point(),
            LegName.FR: self.legs[LegName.FR].get_hip_point(),
            LegName.BR: self.legs[LegName.BR].get_hip_point(),
        }

    def get_leg_coordinates(self) -> dict[LegName, list[Point]]:
        """
        Return coordinates of each leg as a dict containing 4 sets of 4 leg points
        """

        return {
            LegName.BL: self.legs[LegName.BL].get_leg_points(),
            LegName.FL: self.legs[LegName.FL].get_leg_points(),
            LegName.FR: self.legs[LegName.FR].get_leg_points(),
            LegName.BR: self.legs[LegName.BR].get_leg_points(),
        }
    

    def get_foot_points(self) -> dict[LegName, Point]:
        """
        Return coordinates of each leg's foot as a dict containing a point
        """

        return {
            LegName.BL: self.legs[LegName.BL].get_foot_point(),
            LegName.FL: self.legs[LegName.FL].get_foot_point(),
            LegName.FR: self.legs[LegName.FR].get_foot_point(),
            LegName.BR: self.legs[LegName.BR].get_foot_point(),
        }


    def get_joint_angles(self, units: AngleUnits):
        """Get the joint angles for all four legs
        Args:
            units: degrees or radians
        Returns:
            joint_angles: dictionary containing four legs and their
            associated angles in the order q1,q2,q3
        """
       
        joint_angles = {}
        for leg in LegName:
            if units is AngleUnits.RADIANS:
                joint_angles[leg] = self.legs[leg].get_leg_angles_in_radians()
            elif units is AngleUnits.DEGREES:            
                joint_angles[leg] = self.legs[leg].get_leg_angles_in_degrees()          

        return joint_angles

    def check_joint_angles(self):
        """Checks the bounds of joint angles
        Args:
            Legs dictionary to check
        Returns:
            None: no error
            string: error (string describes the error)
        """

        for key, leg in self.legs.items():
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


    def check_ground_penetration(self):
        """Checks for joint points penetrating the ground       
        Returns:
            None: no error
            string: error (string describes the error)
        """
        leg_coords = self.get_leg_coordinates()
        for leg_name, points in leg_coords.items():
            for point in points:
                if point.z < -0.001:
                    return f"[{self.tag}] Leg {leg_name} has a joint angle penetrating the ground at [{round(point.x, 3)}, {round(point.y, 3)}, {round(point.z, 3)}]!"
        return None            
    
    
    def set_joint_angles_degrees(self, leg_angles: Dict[LegName, List[float]]):
        ''' Set the joint angles for all four legs for simulation.

        Args:
            Dict of legs containing list of angles as floats in degrees.
            Angles in the order q1,q2,q3.
        '''

        # Convert all angles in degrees to radians.
        for leg, angles in leg_angles.items():
            leg_angles[leg] = [radians(angle) for angle in angles]

        # Apply the angles to the legs.
        for leg, joint_angles in leg_angles.items():
            self.legs[leg].set_angles(joint_angles[0],joint_angles[1],joint_angles[2])
          
    
    ###############################################################################
    # Getters / Setters
    ###############################################################################

    def get_num_legs(self) -> int:
        return len(self.legs)
    
    def get_joint_angle_error(self) -> bool:
        return self.joint_angle_error
    
    def get_ik_error(self) -> bool:
        return self.ik_error
