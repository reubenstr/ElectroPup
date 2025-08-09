import numpy as np
from enum import Enum, StrEnum
from typing import Dict, List
from quadruped.quad import LegName
from quadruped.point import Point


class Gait(StrEnum):
    NONE = "none"
    CRAWL = "crawl"
    TROT = "trot"

class SwingPattern(StrEnum):
    BEZIER = "beizer"
    SIN = "sin"
   

class Phase(Enum):
    STANCE = 0
    SWING = 1


class GaitPlanner:
    def __init__(self, gait: Gait, swing_pattern: SwingPattern, period: float, duty_factor: float, stride_length: float, step_height: float, phase_offsets: Dict[LegName, float]):
        self.gait = gait

        self.swing_pattern = swing_pattern

        # Duration of one complete gait cycle (seconds).
        self.period = period

        # Percent of time in stand (power stroke).
        # Range: [0, 1].
        # Example: 0.75 = 75% stance, 25% swing
        self.duty_factor = duty_factor

        # Length of the path.
        self.stride_length = stride_length

        # Height of the path.
        self.step_height = step_height

        # Dict[LegName, float] determines when during the gait cycle that leg begins the swing phase.
        # Range: [0, 1],
        self.phase_offsets = phase_offsets

    def get_leg_phase_time(self, leg: LegName, time: float) -> tuple[Phase, float]:
        """Determines the phase and location (time) of the leg."""
        cycle_time = time % self.period
        phase_time = (cycle_time / self.period - self.phase_offsets[leg]) % 1.0
        phase = Phase.STANCE if phase_time < self.duty_factor else Phase.SWING

        # Normalize phase time, example:
        # STANCE: [0, duty_factor]
        # SWING : [duty_factor, 1.0]
        normalized_time = phase_time / self.duty_factor if phase == Phase.STANCE else (phase_time - self.duty_factor) / (1 - self.duty_factor)

        return phase, normalized_time

    def foot_trajectory_bezier(self, phase: Phase, phase_time: float):
        """Return foot (d: distance, h: height) using Bezier swing and linear stance."""

        def bezier_curve(t, points):
            """Evaluate a Bezier curve at t ∈ [0, 1] using De Casteljau's algorithm."""
            p = np.array(points)
            while len(p) > 1:
                p = (1 - t) * p[:-1] + t * p[1:]
            return p[0]

        if phase == Phase.STANCE:
            # Linear backward motion (stroke)
            d = (1 - phase_time) * self.stride_length - self.stride_length / 2
            h = 0
        elif phase == Phase.SWING:
            # Bezier swing (retract/touchdown)
            control_points = np.array(
                [
                    [-self.stride_length / 2, 0],
                    [-self.stride_length, 0],
                    [-self.stride_length, self.step_height],
                    [0, self.step_height],
                    [self.stride_length, self.step_height],
                    [self.stride_length, 0],
                    [self.stride_length / 2, 0],
                ]
            )
            d, h = bezier_curve(phase_time, control_points)
        return d, h

    def foot_trajectory_sin(self, phase: Phase, phase_time: float):
        """Return foot (d: distance, h: height) based on phase and normalized phase time (0-1)."""
        if phase == Phase.STANCE:
            # Stance: foot moves backward linearly along x, stays on ground
            d = (1 - phase_time) * self.stride_length - self.stride_length / 2
            h = 0
        else:
            # Swing: foot moves forward with parabolic height
            d = phase_time * self.stride_length - self.stride_length / 2
            h = self.step_height * np.sin(np.pi * phase_time)
        return d, h

    def get_foot_position(self, leg: LegName, gait_time: float) -> Dict[LegName, Point]:
        phase, phase_time = self.get_leg_phase_time(leg, gait_time)
        if self.swing_pattern is SwingPattern.BEZIER:
            d, h = self.foot_trajectory_bezier(phase, phase_time)
        elif self.swing_pattern is SwingPattern.SIN:
            d, h = self.foot_trajectory_sin(phase, phase_time)
        return Point(d, 0, h)
    

    def get_gait(self) -> Gait:
        return self.gait