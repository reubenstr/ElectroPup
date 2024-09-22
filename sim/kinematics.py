
'''
    Contains kinematic model to generate joint angles from orientation, position, feet location.
'''

import numpy as np
from matrix_transforms import RpToTrans, TransToRp, TransInv, RPY, TransformVector
from collections import OrderedDict


class Kinematics:
    def __init__(self, frame_parameters):

        self.com_offset = frame_parameters['com_offset']

        # Leg Parameters
        self.shoulder_length = frame_parameters['shoulder_length']
        self.upper_leg_length = frame_parameters['upper_leg_length']
        self.lower_leg_length = frame_parameters['lower_leg_length']

        # Leg Vector desired_positions

        # Distance Between Hips
        # Length
        self.hip_x = frame_parameters['hip_x']
        # Width
        self.hip_y = frame_parameters['hip_y']

        # Distance Between Feet
        # Length
        self.foot_x = frame_parameters['foot_x']
        # Width
        self.foot_y = frame_parameters['foot_y']

        # Body Height
        self.height = frame_parameters['height']

        # Rotation from world frame to body frame      
        Rwb = np.eye(3)

        # Transform of Hip relative to world frame with body Centroid also in world frame     
        self.WorldToHip = OrderedDict()       
        self.WorldToHip["FL"] = RpToTrans(Rwb, np.array([self.hip_x / 2.0, self.hip_y / 2.0, 0]))     
        self.WorldToHip["FR"] = RpToTrans(Rwb, np.array([self.hip_x / 2.0, -self.hip_y / 2.0, 0]))     
        self.WorldToHip["BL"] = RpToTrans(Rwb, np.array([-self.hip_x / 2.0, self.hip_y / 2.0, 0]))     
        self.WorldToHip["BR"] = RpToTrans(Rwb, np.array([-self.hip_x / 2.0, -self.hip_y / 2.0, 0]))

        # Transform of Foot relative to world frame with body Centroid also in world frame
        self.WorldToFoot = OrderedDict()
        self.WorldToFoot["FL"] = RpToTrans(Rwb, np.array([self.foot_x / 2.0, self.foot_y / 2.0, -self.height]))
        self.WorldToFoot["FR"] = RpToTrans(Rwb, np.array([self.foot_x / 2.0, -self.foot_y / 2.0, -self.height]))
        self.WorldToFoot["BL"] = RpToTrans(Rwb, np.array([-self.foot_x / 2.0, self.foot_y / 2.0, -self.height]))
        self.WorldToFoot["BR"] = RpToTrans(Rwb, np.array([-self.foot_x / 2.0, -self.foot_y / 2.0, -self.height]))


    def _hip_to_foot(self, orn, pos, T_bf):
        """
        Converts a desired position and orientation from
        home position, with a desired body-to-foot Transform
        into a body-to-hip Transform, which is used to extract
        and return the Hip To Foot Vector.

        :param orn: A 3x1 np.array([]) of Roll, Pitch, Yaw angles
        :param pos: A 3x1 np.array([]) of X, Y, Z coordinates
        :param T_bf: Dictionary of desired body-to-foot Transforms.
        :return: Hip To Foot Vector for each leg.
        """

        # only get rotation component
        rotation_matrix, _ = TransToRp(RPY(orn[0], orn[1], orn[2]))
        position_vector = pos
        T_wb = RpToTrans(rotation_matrix, position_vector)

        # Dictionary to store vectors
        HipToFoot_List = OrderedDict()

        for i, (key, T_wh) in enumerate(self.WorldToHip.items()):
            # ORDER: FL, FR, BL, BR

            # Extract vector component
            _, p_bf = TransToRp(T_bf[key])

            # Step 1, get T_bh for each leg
            T_bh = np.dot(TransInv(T_wb), T_wh)

            # Step 2, get T_hf for each leg

            # VECTOR ADDITION METHOD
            _, p_bh = TransToRp(T_bh)
            p_hf0 = p_bf - p_bh

            # TRANSFORM METHOD
            T_hf = np.dot(TransInv(T_bh), T_bf[key])
            _, p_hf1 = TransToRp(T_hf)

            # They should yield the same result
            if p_hf1.all() != p_hf0.all():
                print("NOT EQUAL")

            p_hf = p_hf1

            HipToFoot_List[key] = p_hf

        return HipToFoot_List

    def _get_domain(self, x, y, z):
        """
        Calculates the leg's Domain and caps it in case of a breach

        :param x,y,z: hip-to-foot distances in each dimension
        :return: Leg Domain D
        """
        D = (y**2 + (-z)**2 - self.shoulder_length**2 +
             (-x)**2 - self.upper_leg_length**2 - self.lower_leg_length**2) / (
                 2 * self.lower_leg_length * self.upper_leg_length)

        #if D > 1 or D < -1:           
        #    print("---------DOMAIN BREACH---------")           
        
        return np.clip(D, -1.0, 1.0)

    def _solve_joint_angles(self, xyz_coord, legType):
        """
        Leg Inverse Kinematics Solver

        :param xyz_coord: hip-to-foot distances in each dimension
        :param legType: leg type to determine orientation
        :return: Joint Angles required for desired position
        """
        x = xyz_coord[0]
        y = xyz_coord[1]
        z = xyz_coord[2]
        D = self._get_domain(x, y, z)

        if legType == "FR" or legType == "BR":
            shoulder_direction_offset = -1
        elif legType == "FL" or legType == "BL":
            shoulder_direction_offset = 1

        lower_leg_angle = np.arctan2(-np.sqrt(1 - D**2), D)
        sqrt_component = y**2 + (-z)**2 - self.shoulder_length**2

        if sqrt_component < 0.0:
            sqrt_component = 0.0

        shoulder_angle = -np.arctan2(z, y) - np.arctan2(
            np.sqrt(sqrt_component), shoulder_direction_offset * self.shoulder_length)

        upper_leg_angle = np.arctan2(-x, np.sqrt(sqrt_component)) - np.arctan2(
            self.lower_leg_length * np.sin(lower_leg_angle),
            self.upper_leg_length + self.lower_leg_length * np.cos(lower_leg_angle))
   
        joint_angles = np.array([-shoulder_angle, upper_leg_angle, lower_leg_angle])

        return joint_angles

    def inverse_kinematics(self, orn, pos, T_bf):
        """
        Uses HipToFoot() to convert a desired position
        and orientation into a Hip To Foot Vector, 
        which is fed into the LegIK solver.

        Finally, the resultant joint angles are returned
        from the LegIK solver for each leg.

        :param orn: A 3x1 np.array([]) with roll, pitch, yaw angles
        :param pos: A 3x1 np.array([]) with X, Y, Z coordinates
        :param T_bf: Dictionary of desired body-to-foot transforms.
        :return: Joint angles for each joint.
        """

        # Modify x by com offset
        pos[0] += self.com_offset

        # 4 legs, 3 joints per leg
        joint_angles = np.zeros((4, 3))

        # Steps 1 and 2 of pipeline
        HipToFoot = self._hip_to_foot(orn, pos, T_bf)

        for i, (key, p_hf) in enumerate(HipToFoot.items()):
            # Step 3, compute joint angles from T_hf for each leg
            joint_angles[i, :] = self._solve_joint_angles(p_hf, key)

        return joint_angles.flatten()
