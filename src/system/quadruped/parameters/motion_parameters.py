import copy
import numpy as np
from enum import Enum
from dataclasses import dataclass
from math import degrees, atan2, sqrt

"""
    Class containing motion parameters for movement.
"""

class MotionParameters:
    def __init__(self):     
        ###############################################################################
        # 
        ###############################################################################
        self.deadzone = 0.025


        ###############################################################################
        # Running values, do not change, will be overwritten
        ###############################################################################
        self.forward_raw : float = 0
        self.heading_degrees: float = 0
        self.heading_magnitude: float = 0
        self.heading_raw: float = 0
        self._heading_x: float = 0
        self._heading_y: float = 0

        

    ###############################################################################
    # Call from the Input class to set values
    ###############################################################################

    def update_forward_raw(self, value : float):
        self.forward_raw = value
    
    def update_heading_x(self, value: float):
        self._heading_x = value
        self.heading_raw = value

    def update_heading_y(self, value: float):
        self._heading_y = value

    ###############################################################################
    # Getters / Setters
    ###############################################################################

    def get_forward_raw(self) -> float:
        """
        Returns value ranged -1.0 to 1.0 representing an gamepad axis
        """
        return self.forward_raw   
    
    def get_forward_direction(self) -> bool:       
        return True if self.forward_raw > 0 else False
       
    def get_heading_raw(self) -> float:
        """
        Returns value ranged -1.0 to 1.0 representing an gamepad axis
        """
        return self.heading_raw

    def get_heading_degrees(self):
        return degrees(atan2(self._heading_x, self._heading_y))

    def get_heading_magnitude(self):
        return sqrt((self._heading_x) ** 2 + (self._heading_y) ** 2)


