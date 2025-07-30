from dataclasses import dataclass

"""
   Class container parameters for pose.
"""

@dataclass
class IKParameters:  
    ###############################################################################
    # Rotation limits parameters (degrees)
    ###############################################################################
    roll_min: float = -30
    roll_max: float = 30
    pitch_min: float = -30
    pitch_max: float = 30
    yaw_min: float = -30
    yaw_max: float = 30

    ###############################################################################
    # Translation limits parameters (meters)
    ###############################################################################
    forward_translation_min: float = -0.050
    forward_translation_max: float = 0.050
    side_translation_min: float = -0.100
    side_translation_max: float = 0.100

    # Lowest allowable point of body center.
    height_translation_min: float = 0.050

    # Highest allowable position of body center, must no be higher than the physical leg lengths.
    height_translation_max: float = 0.250



    ###############################################################################
    # Running values, do not change, will be overwritten
    ###############################################################################
    roll: float = 0
    pitch: float = 0
    yaw: float = 0
    forward_translation: float = 0
    side_translation: float = 0
    height_translation: float = (height_translation_min + height_translation_max) / 2.0
   