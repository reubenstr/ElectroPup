from dataclasses import dataclass
from . utilities import process_value, check_value, scale_value

"""
   Class container parameters for pose.

   If dynamic control is added to forward or side transation, ensure to add the forward_compensation.
"""


@dataclass
class IKParameters:
    ###############################################################################
    # Rotation limits parameters (degrees) Can be modified
    ###############################################################################
    roll_min: float = -30
    roll_max: float = 30
    pitch_min: float = -25
    pitch_max: float = 25
    yaw_min: float = -30
    yaw_max: float = 30

    ###############################################################################
    # Translation limits parameters (meters) Can be modified
    ###############################################################################
    forward_translation_min: float = -0.050
    forward_translation_max: float = 0.050

    # Add a permanent forward translation to move the center of mass in a more stable position.
    forward_compensation: float = 0.0

    side_translation_min: float = -0.075
    side_translation_max: float = 0.075

    # Highest allowable position of body center, must no be higher than the physical leg lengths.
    height_translation_max: float = 0.275

    # Desired height for the neutral position (no user input).
    height_translation_neutral: float = 0.2

    # Lowest allowable point of body center.
    height_translation_min: float = 0.04

    ###############################################################################
    # Default running values, do not change, values will be overwritten
    ###############################################################################
    roll: float = 0
    pitch: float = 0
    yaw: float = 0
    forward_translation: float = forward_compensation
    side_translation: float = 0
    height_translation: float = height_translation_neutral

    ###############################################################################
    # Misc parameters
    ###############################################################################
    deadzone = 0.025

    ###############################################################################
    # Getters / Setters
    ###############################################################################

    def set_roll(self, value: float):   
        self.roll = scale_value(process_value(-value, self.deadzone), -1, 1, self.roll_min, self.roll_max)

    def set_pitch(self, value: float):   
        self.pitch = scale_value(process_value(-value, self.deadzone), -1, 1, self.pitch_min, self.pitch_max)

    def set_yaw(self, value: float):
        self.yaw = scale_value(process_value(value, self.deadzone), -1, 1, self.yaw_min, self.yaw_max)

    def set_forward_translation(self, value: float):
        self.forward_translation = scale_value(process_value(value, self.deadzone), -1, 1, self.forward_translation_min, self.forward_translation_max)

    def set_side_translation(self, value: float):
        self.side_translation = scale_value(process_value(value, self.deadzone), -1, 1, self.side_translation_min, self.side_translation_max)

    def set_height_translation(self, value: float):
        value = process_value(-value, self.deadzone)   
        if value < 0:
            self.height_translation = scale_value(value, -1, 0, self.height_translation_min, self.height_translation_neutral)
        else:
            self.height_translation = scale_value(value, 0, 1, self.height_translation_neutral, self.height_translation_max)

  