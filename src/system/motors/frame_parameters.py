"""
Class containing frame parameters for quadruped rotation, translation, and states.
"""

class FrameParameters:
    def __init__(self):   

        # Frame dimensions (meters):
        # L1, distance hip pivot center of rotation to upper leg rotation joint
        self.hip_length = 0.036

        # L2, upper leg length between both pivot points
        self.upper_leg_length = 0.140

        # L3, lower leg length from pivot point to foot ground contact point
        self.lower_leg_length = 0.140

        # distance between left and right hip pivot center of rotation
        self.body_width = 0.150

        # distance between front and rear hip pivot center of rotation
        self.body_length = 0.338

        # distance between front and back foot centers at ground touch
        self.foot_length = 0.338

        # distance between left and right foot centers at ground touch
        self.foot_width = 0.261

        # Joint bounds (degrees):
        self.abduction_joint_lower_bounds = -45.0
        self.abduction_joint_upper_bounds = 45.0
        self.hip_joint_lower_bounds = -100.0
        self.hip_joint_upper_bounds = 90.0
        self.knee_joint_lower_bounds = -180.0
        self.knee_joint_upper_bounds = 180.0
