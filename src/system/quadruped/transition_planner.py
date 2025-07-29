import numpy as np
from math import cos, pi, sin
from enum import Enum, StrEnum
from typing import Dict, List
from system.quadruped.quad import LegName
from system.quadruped.point import Point, get_distance_xyz


class Phase(Enum):
    LOWER = 0
    REPLACE = 1


"""
TransitionPlanner(
    period=1.0,
    duty_factor=0.75,
    phase_offsets={
        LegName.FL: 0.0,
        LegName.BR: 0.25,
        LegName.FR: 0.5,
        LegName.BL: 0.75,
    },
"""


class TransitionPlanner:
    def __init__(self, period: float, duty_factor: float, phase_offsets: Dict[LegName, float]):

        # Duration of one complete gait cycle (seconds).
        self.period = period

        # Percent of time in stand (power stroke).
        # Range: [0, 1].
        # Example: 0.75 = 75% stance, 25% swing
        self.duty_factor = duty_factor

        # Dict[LegName, float] determines when during the gait cycle that leg begins the swing phase.
        # Range: [0, 1],
        self.phase_offsets = phase_offsets

    def get_leg_phase_time(self, leg: LegName, time: float) -> tuple[Phase, float]:
        """Determines the phase and location (time) of the leg."""
        cycle_time = time % self.period
        phase_time = (cycle_time / self.period - self.phase_offsets[leg]) % 1.0
        phase = Phase.LOWER if phase_time < self.duty_factor else Phase.REPLACE

        # Normalize phase provides a value [0, 1] within the respective phase:
        # STANCE: [0, duty_factor]
        # SWING : [duty_factor, 1.0]
        normalized_time = phase_time / self.duty_factor if phase == Phase.LOWER else (phase_time - self.duty_factor) / (1 - self.duty_factor)
        return phase, normalized_time

    def foot_trajectory_sin(self, phase: Phase, phase_time: float, active_foot_point: Point, target_foot_position: Point, step_height=0.05):

        def sin_arc_transition(start: Point, end: Point, time_phase: float, height: float) -> Point:
            """Create an arc in the z between two xy points."""
            x = start.x + (end.x - start.x) * time_phase
            y = start.y + (end.y - start.y) * time_phase
            z_linear = start.z + (end.z - start.z) * time_phase
            arc_offset = height * sin(pi * time_phase)
            z = z_linear + arc_offset
            return Point(x, y, z)

        if phase == Phase.LOWER:
            #  Lower foot directly down from the active to target position.
            z_distance = active_foot_point.z - target_foot_position.z
            return Point(active_foot_point.x, active_foot_point.y, (1 - phase_time) * z_distance)
        else:
            # Create arc transition between the active and target positions.
            height = 0.050
            return sin_arc_transition(active_foot_point, target_foot_position, phase_time, height)
