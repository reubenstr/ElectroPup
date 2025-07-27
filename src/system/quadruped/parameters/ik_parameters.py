"""
    User inputs that modify the rotation and translation of the hexapod.
    Edit these values to prevent inputs that cause positional errors.
"""

class IKParameters:  
    # Rotation limits in degrees:
    rotate_x_min: float = -30
    rotate_x_max: float = 30
    rotate_y_min: float = -45
    rotate_y_max: float = 45
    rotate_z_min: float = -45
    rotate_z_max: float = 45

    # Translation limits in millimeters:
    translate_x_min: float = -100
    translate_x_max: float = 100
    translate_y_min: float = -100
    translate_y_max: float = 100
    translate_z_min: float = -100
    translate_z_max: float = 100

    # Do not change, will be overwritten:
    translate_x: float = 0
    translate_y: float = 0
    translate_z: float = 0
    rotate_x: float = 0
    rotate_y: float = 0
    rotate_z: float = 0