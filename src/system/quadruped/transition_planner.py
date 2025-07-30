from math import pi, sin
from enum import Enum
from typing import Dict
import numpy as np
from system.quadruped.quad import LegName
from system.quadruped.point import Point
from system.quadruped.interfaces import Trajectories, Trajectory


class Phase(Enum):
    TOUCHDOWN = 0
    ARC = 1
    IDLE = 2
    COMPLETE = 3


class TransitionPlanner:
    def __init__(
        self,
        touchdown_period: float,
        arc_period: float,
        height,
    ):
        self.touchdown_period = touchdown_period
        self.arc_period = arc_period
        self.height = height    

    def get_phase_index_and_phase_time(self, time: float, period: float, num_phases: int):
        section_length = period / num_phases
        time_wrapped = time % period
        phase_index = int(time_wrapped // section_length)
        phase_start = phase_index * section_length
        phase_time = (time_wrapped - phase_start) / section_length
        return phase_index, phase_time

    def get_leg_phase_time(self, leg: LegName, time: float) -> tuple[Phase, float]:
        """Determines the phase and location (time) of the leg."""
        leg_index = list(LegName).index(leg)
        num_legs = len(LegName)
        cycle_time = time % self.get_period()

        if cycle_time < self.touchdown_period:
            phase = Phase.TOUCHDOWN
            normalized_time = cycle_time / self.touchdown_period
        else:
            phase_index, phase_time = self.get_phase_index_and_phase_time(
                cycle_time - self.touchdown_period, self.get_period() - self.touchdown_period, num_legs
            )
            if leg_index == phase_index:
                phase = Phase.ARC
                normalized_time = phase_time
            elif leg_index > phase_index:
                phase = Phase.IDLE
                normalized_time = None
            else:
                phase = Phase.COMPLETE
                normalized_time = None

        return phase, normalized_time

    def foot_trajectory_sin(self, phase: Phase, phase_time: float, start_point: Point, end_point: Point):
        def sin_arc_transition(start: Point, end: Point, time_phase: float, height: float) -> Point:
            """Create an arc in the z between two xy points."""
            x = start.x + (end.x - start.x) * time_phase
            y = start.y + (end.y - start.y) * time_phase
            z = height * sin(pi * time_phase)
            return Point(x, y, z)

        if phase == Phase.TOUCHDOWN:
            # Lower foot directly down from the start points to height of the end points.
            z_distance = start_point.z - end_point.z
            return Point(start_point.x, start_point.y, (1 - phase_time) * z_distance)
        elif phase == Phase.ARC:
            # Create arc transition between the start and end points.
            return sin_arc_transition(start_point, end_point, phase_time, self.height)
        elif phase == Phase.IDLE:            
            return Point(start_point.x, start_point.y, 0)
        else:
            return end_point

    def get_foot_positions(self, time: float, start_foot_points: Dict[LegName, Point], end_foot_points: Dict[LegName, Point]) -> Dict[LegName, Point]:
        foot_points: Dict[LegName, Point] = {}
        for leg in LegName:
            start_foot_point = start_foot_points[leg]
            end_foot_point = end_foot_points[leg]
            phase, phase_time = self.get_leg_phase_time(leg, time)
            foot_points[leg] = self.foot_trajectory_sin(phase, phase_time, start_foot_point, end_foot_point)
        return foot_points

    def get_transitions(self, start_foot_points: Dict[LegName, Point], end_foot_points: Dict[LegName, Point]):
        """Generate transitions for visual representation"""

        if start_foot_points == {} or end_foot_points == {}:
            return None
       
        timestep = self.get_period() / 100
        phase_times = np.arange(0, self.get_period(), timestep)

        trajectories: Trajectories = []

        for leg in LegName:
            start_foot_point = start_foot_points[leg]
            end_foot_point = end_foot_points[leg]

            trajectory: Trajectory = []
            for phase_time in phase_times:
                phase, phase_time = self.get_leg_phase_time(leg, phase_time)
                foot_point = self.foot_trajectory_sin(phase, phase_time, start_foot_point, end_foot_point)
                trajectory.append(foot_point)
            trajectories.append(trajectory)

        return trajectories

    ###############################################################################
    # Getters / Setters
    ###############################################################################

    def get_period(self):
        return self.touchdown_period + self.arc_period * len(LegName)
