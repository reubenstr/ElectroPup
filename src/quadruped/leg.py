from math import pi, degrees
import numpy as np
from . import kinematics
from . import transformations

class Leg(object):
    '''Encapsulates a leg that consists of 3 links and 3 joint angles
    
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
        _leg12: Boolean specifying whether leg is 1 or 2 (rightback or rightfront)
                or 3 or 4 (leftfront or leftback)  
    '''

    def __init__(self,q1,q2,q3,l1,l2,l3,ht_leg_start,leg12):
        '''Constructor'''
        self._q1 = q1
        self._q2 = q2
        self._q3 = q3
        self._l1 = l1
        self._l2 = l2
        self._l3 = l3
        self._ht_leg_start = ht_leg_start
        self._leg12 = leg12

        # Create homogeneous transformation matrices for each joint
        self._t01 = kinematics.t_0_to_1(self._q1,self._l1)
        self._t12 = kinematics.t_1_to_2()
        self._t23 = kinematics.t_2_to_3(self._q2,self._l2)
        self._t34 = kinematics.t_3_to_4(self._q3,self._l3)


    def set_angles(self,q1,q2,q3):
        '''Set the three leg angles and update transformation matrices as needed'''
        self._q1 = q1
        self._q2 = q2
        self._q3 = q3
        self._t01 = kinematics.t_0_to_1(self._q1,self._l1)
        self._t23 = kinematics.t_2_to_3(self._q2,self._l2)
        self._t34 = kinematics.t_3_to_4(self._q3,self._l3)
    
    def set_homog_transf(self,ht_leg_start):
        '''Set the homogeneous transformation of the leg start position'''
        self._ht_leg_start = ht_leg_start

    def get_homog_transf(self):
        '''Return this leg's homogeneous transformation of the leg start position'''
        return self._ht_leg_start

    def set_foot_position_in_local_coords(self,x4,y4,z4):
        '''Set the position of the foot by computing joint angles via inverse kinematics from inputted coordinates.
        Leg's coordinate frame is the frame defined by self._ht_leg_start

        Args:
            x4: Desired foot x position in leg's coordinate frame
            y4: Desired foot y position in leg's coordinate frame
            z4: Desired foot z position in leg's coordinate frame
        Returns:
            Nothing
        '''
        # Run inverse kinematics and get joint angles
        leg_angs = kinematics.ikine(x4,y4,z4,self._l1,self._l2,self._l3,self._leg12)

        # Call method to set joint angles for leg
        self.set_angles(leg_angs[0],leg_angs[1],leg_angs[2])

    def set_foot_position_in_global_coords(self,x4,y4,z4):
        ''' Set the position of the foot by computing joint angles via inverse kinematics from inputted coordinates.
        Inputted coordinates in the global coordinate frame

        Args:
            x4: Desired foot x position in global coordinate frame
            y4: Desired foot y position in global coordinate frame
            z4: Desired foot z position in global coordinate frame
        Returns:
            Nothing
        '''
        # Get inverse of leg's homogeneous transform
        ht_leg_inv = transformations.ht_inverse(self._ht_leg_start)

        # Convert the foot coordinates for use with homogeneous transforms, e.g.:
        # p4 = [x4, y4, z4, 1]
        p4_global_coord = np.block( [np.array([x4, y4, z4]), np.array([1])])

        # Calculate foot coordinates in each leg's coordinate system
        p4_in_leg_coords = ht_leg_inv.dot(p4_global_coord) 

        # Call this leg's position set function for coordinates in local frame
        self.set_foot_position_in_local_coords(p4_in_leg_coords[0],p4_in_leg_coords[1],p4_in_leg_coords[2])


    def get_leg_points(self):
        '''Get coordinates of 4 points that define a wireframe of the leg:
            Point 1: hip/body point
            Point 2: upper leg/hip joint
            Point 3: Knee, (upper/lower leg joint)
            Point 4: Foot, leg end
        
        Returns:
            A length 4 tuple consisting of 4 length 3 numpy arrays representing the 
            x,y,z coordinates in the global frame of the 4 leg points
        '''
        # Build up the total homogeneous transformation incrementally, saving each leg
        # point along the way
        # The total homogeneous transformation builup is:
        # ht = ht_leg_start @ t01 @ t12 @ t23 @ t34 
        p1 = self._ht_leg_start[0:3,3]

        # ht_buildup = self._ht_leg_start @ self._t01 @ self._t12
        ht_buildup = np.matmul(np.matmul(self._ht_leg_start, self._t01), self._t12)

        p2 = ht_buildup[0:3,3]

        # ht_buildup = ht_buildup @ self._t23
        ht_buildup = np.matmul(ht_buildup, self._t23)
        
        p3 = ht_buildup[0:3,3]

        # ht_buildup = ht_buildup @ self._t34
        ht_buildup = np.matmul(ht_buildup, self._t34)

        p4 = ht_buildup[0:3,3]

        return (p1,p2,p3,p4)

    def get_foot_position_in_global_coords(self):
        ''' Return coordinates of the foot in the leg's local coordinate frame'''
        ht_foot = np.matmul(np.matmul(np.matmul(np.matmul(self._ht_leg_start, self._t01), self._t12), self._t23), self._t34)
        return ht_foot[0:3,3]
    
    def get_leg_angles_in_radians(self):
        '''Return leg angles as a tuple of 3 angles, (q1, q2, q3)'''
        return (self._q1,self._q2,self._q3)
    
    def get_leg_angles_in_degrees(self):
        '''Return leg angles in degrees as a dictionary as q1,q2,q3 ''' 
        return {'abduction':degrees(self._q1), 'hip':degrees(self._q2), 'knee':degrees(self._q3)}