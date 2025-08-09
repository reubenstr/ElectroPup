import copy
import numpy as np
from enum import Enum
from time import time
from dataclasses import dataclass
from math import degrees, atan2, sqrt
from .utilities import process_value, check_value, scale_value

"""
    Class containing motion parameters for movement.

    Class handles deadzone.
"""

@dataclass
class MotionParameters:

    ###############################################################################
    # Running values, do not change, will be overwritten
    ###############################################################################
    _forward_velocity: float = 0
    _lateral_velocity: float = 0
    _angular_velocity: float =0

    ###############################################################################
    # Misc. Parameters
    ###############################################################################
    deadzone: float = 0.040

    ###############################################################################
    # Getters / Setters
    ###############################################################################

    @property
    def forward_velocity(self):
        return self._forward_velocity
    
    @forward_velocity.setter
    def forward_velocity(self, value):
        self._forward_velocity = process_value(-value, self.deadzone)

    @property
    def lateral_velocity(self):
        return self._lateral_velocity
    
    @lateral_velocity.setter
    def lateral_velocity(self, value):
        self._lateral_velocity = process_value(value, self.deadzone)

    @property
    def angular_velocity(self):
        return self._angular_velocity
   
    @angular_velocity.setter
    def angular_velocity(self, value):
        self._angular_velocity = process_value(-value, self.deadzone)      

    ###############################################################################
    # Heading
    ###############################################################################

    '''def set_heading_x(self, value: float):
        self._heading_x = process_value(-value, self.deadzone)
        self._heading_raw = process_value(-value, self.deadzone)

    def set_heading_y(self, value: float):
        self._heading_y = process_value(value, self.deadzone)

    def get_heading_raw(self) -> float:
        return self._heading_raw

    def get_heading_degrees(self):
        return degrees(atan2(self._heading_x, self._heading_y))

    def get_heading_magnitude(self):
        return sqrt((self._heading_x) ** 2 + (self._heading_y) ** 2)'''


    def slew_heading(
        self,
        heading: float,        
        last_time: float,
        heading_rate_seconds: float
    ) -> tuple[float, float]:
        """
        Provides heading with a time-based ramp.
        
        Args:
            heading: Current heading value.           
            last_time: Time of previous update (in seconds).
            heading_rate_seconds: Time to ramp from 0 to 1 or -1.
        
        Returns:
            Tuple of (new_heading, current_time)
        """
        current_time = time()
        dt = current_time - last_time
        max_delta = dt / heading_rate_seconds

        delta = self._angular_velocity - heading

        if abs(delta) <= max_delta:
            heading = self._angular_velocity
        else:
            heading += max_delta * (1 if delta > 0 else -1)

        return heading, current_time