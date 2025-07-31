from dataclasses import dataclass

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
    pitch_min: float = -30
    pitch_max: float = 30
    yaw_min: float = -30
    yaw_max: float = 30

    ###############################################################################
    # Translation limits parameters (meters) Can be modified
    ###############################################################################
    forward_translation_min: float = -0.050
    forward_translation_max: float = 0.050
    side_translation_min: float = -0.050
    side_translation_max: float = 0.050

    # Highest allowable position of body center, must no be higher than the physical leg lengths.
    height_translation_max: float = 0.275

    # Desired height for the neutral position (no user input).
    height_translation_neutral: float = 0.2

    # Lowest allowable point of body center.
    height_translation_min: float = 0.04

    ###############################################################################
    # Default running values, do not change, will be overwritten
    ###############################################################################
    roll: float = 0
    pitch: float = 0
    yaw: float = 0
    forward_translation: float = 0
    side_translation: float = 0
    height_translation: float = height_translation_neutral
    height_translation_raw: float = 0

    ###############################################################################
    # Getters / Setters
    ###############################################################################

    def set_roll(self, value: float):
        self.check_value(value)
        self.roll = self.scale_value(value, -1, 1, self.roll_min, self.roll_max)

    def set_pitch(self, value: float):
        self.check_value(value)
        self.pitch = self.scale_value(value, -1, 1, self.pitch_min, self.pitch_max)

    def set_yaw(self, value: float):
        self.check_value(value)
        self.yaw = self.scale_value(value, -1, 1, self.yaw_min, self.yaw_max)

    def set_forward_translation(self, value: float):
        self.check_value(value)
        self.forward_translation = self.scale_value(value, -1, 1, self.forward_translation_min, self.forward_translation_max)

    def set_side_translation(self, value: float):
        self.check_value(value)
        self.side_translation = self.scale_value(value, -1, 1, self.side_translation_min, self.side_translation_max)

    def set_height_translation(self, value: float):
        self.check_value(value)
        if value < 0:
            self.height_translation = self.scale_value(value, -1, 0, self.height_translation_min, self.height_translation_neutral)
        else:
            self.height_translation = self.scale_value(value, 0, 1, self.height_translation_neutral, self.height_translation_max)

    @staticmethod
    def check_value(value):
        if value < -1 or value > 1:
            raise ValueError(f"value out of range! {value} is not in [-1, 1]")

    @staticmethod
    def scale_value(value, old_min, old_max, new_min, new_max) -> float:
        if old_max == old_min:
            raise ValueError("old_max and old_min cannot be the same value.")
        return (value - old_min) / (old_max - old_min) * (new_max - new_min) + new_min
