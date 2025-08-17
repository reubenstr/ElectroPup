from time import time
from dataclasses import dataclass
from math import degrees, atan2, sqrt
from .utilities import process_value

"""
    Class containing motion parameters for movement.

    Class handles deadzone.
"""


@dataclass
class MotionParameters:

    ###############################################################################
    # Running values
    ###############################################################################
    _forward_velocity: float = 0 # [-1, 1]
    _lateral_velocity: float = 0 # [-1, 1]
    _angular_velocity: float = 0 # [-1, 1]

    ###############################################################################
    # Misc. Parameters
    ###############################################################################
    deadzone: float = 0.040


    ###############################################################################
    # Set values by axis input in the range [-1, 1]
    ###############################################################################

    def set_forward_velocity_by_axis(self, value):
        self.forward_velocity = process_value(-value, self.deadzone)

    def set_lateral_velocity_by_axis(self, value):
        self.lateral_velocity = process_value(value, self.deadzone)

    def set_angular_velocity_by_axis(self, value):
        self.angular_velocity = process_value(value, self.deadzone)

    ###############################################################################
    # Getters / Setters
    ###############################################################################

    @property
    def forward_velocity(self):
        return self._forward_velocity

    @forward_velocity.setter
    def forward_velocity(self, value):
        self._forward_velocity = value

    @property
    def lateral_velocity(self):
        return self._lateral_velocity

    @lateral_velocity.setter
    def lateral_velocity(self, value):
        self._lateral_velocity = value

    @property
    def angular_velocity(self):
        return self._angular_velocity

    @angular_velocity.setter
    def angular_velocity(self, value):
        self._angular_velocity = value

    ###############################################################################
    # Heading
    ###############################################################################

    def get_heading_degrees(self):
        return degrees(atan2(self._lateral_velocity, self._forward_velocity))

    def get_left_magnitude(self):
        return sqrt((self._lateral_velocity) ** 2 + (self._forward_velocity) ** 2)

    def slew_heading(self, heading: float, last_time: float, heading_rate_seconds: float) -> tuple[float, float]:
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
