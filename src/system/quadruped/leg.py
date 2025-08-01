from math import pi, degrees
import numpy as np
from typing import List, Dict

from . import kinematics
from . import transformations
from quadruped.point import Point


class Leg(object):
    """Encapsulates a leg that consists of 3 links and 3 joint angles

    Attributes:
        _q1: Rotation angle in radians of hip joint
        _q2: Rotation angle in radians of upper leg joint
        _q3: Rotation angle in radians of lower leg joint
        _l1: Length of leg link 1 (i.e.: hip joint)
        _l2: Length of leg link 2 (i.e.: upper leg)
        _l3: Length of leg link 3 (i.e.: lower leg)
        _ht_leg: Homogeneous transformation matrix of leg starting
                 position and coordinate system relative to robot body.
                 4x4 np matrix
        _foot_point: foot position (end effector) that the kinematics will attempt to reach.
        _leg12: Boolean specifying whether leg is 1 or 2 (rightback or rightfront)
                or 3 or 4 (leftfront or leftback)

    Notes:
        Leg calculates in Y up coords. 
        Every point passed to Legs is converted from Z up to Y up
        Evert poiont passed out from legs is converted from Y up to Z up
    """

    def __init__(self, q1, q2, q3, l1, l2, l3, ht_leg_start, foot_point: Point, leg12: bool):
        self._q1 = q1
        self._q2 = q2
        self._q3 = q3
        self._l1 = l1
        self._l2 = l2
        self._l3 = l3
        self._ht_leg_start = ht_leg_start
        self._foot_point: Point = self.swap_point(foot_point)
        self._leg12: bool = leg12

        # Create homogeneous transformation matrices for each joint
        self._t01 = kinematics.t_0_to_1(self._q1, self._l1)
        self._t12 = kinematics.t_1_to_2()
        self._t23 = kinematics.t_2_to_3(self._q2, self._l2)
        self._t34 = kinematics.t_3_to_4(self._q3, self._l3)

        self.calculate_ik()

    def set_angles(self, q1, q2, q3):
        """Set the three leg angles and update transformation matrices as needed"""
        self._q1 = q1
        self._q2 = q2
        self._q3 = q3
        self._t01 = kinematics.t_0_to_1(self._q1, self._l1)
        self._t23 = kinematics.t_2_to_3(self._q2, self._l2)
        self._t34 = kinematics.t_3_to_4(self._q3, self._l3)

    def calculate_ik(self):
        # Get inverse of leg's homogeneous transform
        ht_leg_inv = transformations.ht_inverse(self._ht_leg_start)

        # Convert the foot coordinates for use with homogeneous transforms, e.g.:
        # p4 = [x4, y4, z4, 1]
        p4_global_coord = np.block([np.array([self._foot_point.x, self._foot_point.y, self._foot_point.z]), np.array([1])])

        # Calculate foot coordinates in each leg's coordinate system
        p4_in_leg_coords = ht_leg_inv.dot(p4_global_coord)

        # Run inverse kinematics and get joint angles
        leg_angs = kinematics.ikine(p4_in_leg_coords[0], p4_in_leg_coords[1], p4_in_leg_coords[2], self._l1, self._l2, self._l3, self._leg12)

        # Call method to set joint angles for leg
        self.set_angles(leg_angs[0], leg_angs[1], leg_angs[2])

    def get_hip_point(self) -> Point:
        p1 = Point(*self._ht_leg_start[0:3, 3])
        return self.swap_points([p1])[0]

    def get_leg_points(self) -> List[Point]:
        """Get coordinates of 4 points that define a wireframe of the leg:
            Point 1: hip/body point
            Point 2: upper leg/hip joint
            Point 3: Knee, (upper/lower leg joint)
            Point 4: Foot, leg end

        Returns:
            A length 4 list consisting of 4 length 3 numpy arrays representing the
            x,y,z coordinates in the global frame of the 4 leg points
        """
        # Build up the total homogeneous transformation incrementally, saving each leg
        # point along the way
        # The total homogeneous transformation buildup is:
        # ht = ht_leg_start @ t01 @ t12 @ t23 @ t34

        p1 = Point(*self._ht_leg_start[0:3, 3])

        ht_buildup = np.matmul(np.matmul(self._ht_leg_start, self._t01), self._t12)
        p2 = Point(*ht_buildup[0:3, 3])

        ht_buildup = np.matmul(ht_buildup, self._t23)
        p3 = Point(*ht_buildup[0:3, 3])

        ht_buildup = np.matmul(ht_buildup, self._t34)
        p4 = Point(*ht_buildup[0:3, 3])

        return self.swap_points([p1, p2, p3, p4])

    '''
    def get_foot_position_in_global_coords(self) -> Point:
        """Return coordinates of the foot in the leg's local coordinate frame"""
        ht_foot = np.matmul(np.matmul(np.matmul(np.matmul(self._ht_leg_start, self._t01), self._t12), self._t23), self._t34)
        return self.swap_points([Point(*ht_foot[0:3, 3])])[0]
    '''    

    def get_foot_point(self) -> Point:     
        return self.swap_point(self._foot_point)

    def get_leg_angles_in_radians(self) -> Dict[str, float]:
        """Return leg angles as a dictionary as q1, q2, q3"""
        return {"abduction": self._q1, "hip": self._q2, "knee": self._q3}

    def get_leg_angles_in_degrees(self) -> Dict[str, float]:
        """Return leg angles in degrees as a dictionary as q1,q2,q3"""
        return {"abduction": degrees(self._q1), "hip": degrees(self._q2), "knee": degrees(self._q3)}

    ###############################################################################
    # Helpers
    ###############################################################################

    def swap_points(self, point_list: List[Point]) -> List[Point]:
        """
        Swap values of a list of Point objects to convert Y up to Z up.
        """
        swapped = []
        for pt in point_list:
            swapped.append(Point(pt.x, pt.z, pt.y, pt.name))
        return swapped

    def swap_point(self, point: Point) -> Point:
        """
        Swap values of a list of Point objects to convert Y up to Z up.
        """       
        return Point(point.x, point.z, point.y, point.name)
