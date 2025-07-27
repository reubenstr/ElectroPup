from dataclasses import dataclass

"""
    User inputs that modify the rotation and translation of the hexapod.
    Edit these values to prevent inputs that cause positional errors.
"""

@dataclass
class IKParameters:  
    # Rotation limits in degrees:
    roll_min: float = -30
    roll_max: float = 30
    pitch_min: float = -45
    pitch_max: float = 45
    yaw_min: float = -45
    yaw_max: float = 45

    # Translation limits in millimeters:
    forward_translation_min: float = -100
    forward_translation_max: float = 100
    side_translation_min: float = -100
    side_translation_max: float = 100
    height_translation_min: float = -100
    height_translation_max: float = 100

    # Do not change, will be overwritten:
    forward_translation: float = 0
    side_translation: float = 0
    height_translation: float = 0
    roll: float = 0
    pitch: float = 0
    yaw: float = 0