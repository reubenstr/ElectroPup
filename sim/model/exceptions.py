"""
    Custom exceptions for better error reporting and handling.
"""
import math

class JointOutOfBounds(Exception):
    """Exception raised when joint angle is outside of bounds.

    Attributes:
        joint -- name of joint
        angle -- angle of the joint
        lower_bound -- allowable lower bound angle of the joint
        upper_bound -- allowable upper bound angle of the joint
    """

    def __init__(self, leg, joint, angle, lower_bound, upper_bound):
        self.leg = leg
        self.joint = joint
        self.angle = angle
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.message = f"Leg {leg} at joint {joint} is out of bounds! Angle {math.degrees(angle):0.2f} is outside of [{math.degrees(lower_bound):0.2f}, {math.degrees(upper_bound):0.2f}]"
        super().__init__(self.message)



