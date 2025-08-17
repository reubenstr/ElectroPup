from dataclasses import dataclass
from .utilities import process_value, check_value, scale_value

"""
   Class container parameters for pose.
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
    forward_compensation: float = 0.025

    lateral_translation_min: float = -0.075
    lateral_translation_max: float = 0.075

    # Highest allowable position of body center, must no be higher than the physical leg lengths.
    height_translation_max: float = 0.275

    # Desired height for the neutral position (no user input).
    height_translation_neutral: float = 0.2

    # Lowest allowable point of body center.
    height_translation_min: float = 0.04

    ###############################################################################
    # Running values
    ###############################################################################
    _roll: float = 0
    _pitch: float = 0
    _yaw: float = 0
    _forward_translation: float = 0
    _lateral_translation: float = 0
    _height_translation: float = height_translation_neutral

    ###############################################################################
    # Misc parameters
    ###############################################################################
    deadzone: float = 0.040

    ###############################################################################
    # Set values by axis input in the range [-1, 1]
    ###############################################################################

    def set_roll_by_axis(self, value):
        self.roll = scale_value(process_value(-value, self.deadzone), -1, 1, self.roll_min, self.roll_max)

    def set_pitch_by_axis(self, value):
        self.pitch = scale_value(process_value(-value, self.deadzone), -1, 1, self.pitch_min, self.pitch_max)

    def set_yaw_by_axis(self, value):
        self.yaw = scale_value(process_value(value, self.deadzone), -1, 1, self.yaw_min, self.yaw_max)

    def set_forward_transation_from_axis(self, value):
        self.forward_translation = scale_value(process_value(value, self.deadzone), -1, 1, self.forward_translation_min, self.forward_translation_max)

    def set_lateral_transation_by_axis(self, value):
        self.lateral_translation = scale_value(process_value(value, self.deadzone), -1, 1, self.lateral_translation_min, self.lateral_translation_max)

    def set_height_transition_by_axis(self, value):
        value = process_value(-value, self.deadzone)
        if value < 0:
            self.height_translation = scale_value(value, -1, 0, self.height_translation_min, self.height_translation_neutral)
        else:
            self.height_translation = scale_value(value, 0, 1, self.height_translation_neutral, self.height_translation_max)

    ###############################################################################
    # Getters / Setters
    ###############################################################################

    @property
    def roll(self):
        return self._roll

    @roll.setter
    def roll(self, value):
        self._roll = value

    @property
    def pitch(self):
        return self._pitch

    @pitch.setter
    def pitch(self, value):
        self._pitch = value

    @property
    def yaw(self):
        return self._yaw

    @yaw.setter
    def yaw(self, value):
        self._yaw = value

    @property
    def forward_translation(self):
        return self._forward_translation + self.forward_compensation

    @forward_translation.setter
    def forward_translation(self, value):
        self._forward_translation = value

    @property
    def lateral_translation(self):
        return self._lateral_translation

    @lateral_translation.setter
    def lateral_translation(self, value):
        self._lateral_translation = value

    @property
    def height_translation(self):
        return self._height_translation

    @height_translation.setter
    def height_translation(self, value):
        self._height_translation = value
