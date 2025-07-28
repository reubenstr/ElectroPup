from enum import Enum
from time import time, sleep
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, TypeAlias

from system.quadruped.point import Point
from system.quadruped.quad import Quad
from system.quadruped.gait import GaitPlanner
from system.interfaces import LegName
from system.quadruped.gait import Gait

Trajectory: TypeAlias = List[Point]
Trajectories: TypeAlias = List[Trajectory]


class TrajectoryPlanner:
    def __init__(self):

        self.set_gait(Gait.WALK)
        self.gait_time: float = 0.0

    ###############################################################################
    # Gaits (can be modified)
    ###############################################################################

    def set_gait(self, gait: Gait):
        self.gait_planner: GaitPlanner = self.gait_factory(gait)

    def gait_factory(self, gait: Gait) -> GaitPlanner:
        if gait == Gait.WALK:
            return GaitPlanner(
                name="Walk",
                period=1.0,
                duty_factor=0.75,
                phase_offsets={
                    LegName.FL: 0.0,
                    LegName.BR: 0.25,
                    LegName.FR: 0.5,
                    LegName.BL: 0.75,
                },
            )
        elif gait == Gait.TROT:
            return GaitPlanner(
                name="Trot",
                period=0.6,
                duty_factor=0.5,
                phase_offsets={
                    LegName.FL: 0.0,
                    LegName.BR: 0.0,
                    LegName.FR: 0.5,
                    LegName.BL: 0.5,
                },
            )

    ###############################################################################
    # Methods
    ###############################################################################

    def tick_gait_time(self, dt: float):
        self.gait_time += dt
   
    def get_foot_point(self, leg_name: LegName, base_foot_point: Point):
        phase, phase_time = self.gait_planner.get_leg_phase_time(leg_name, self.gait_time)
        d, h = self.gait_planner.foot_trajectory_bezier(phase, phase_time, stride_length=0.15)
        point = Point(d, 0, h)

        # Move point foot location.
        point.move_xyz(base_foot_point.x, base_foot_point.y, base_foot_point.z)

        return point

    def get_trajectories(self, base_foot_points: Dict[LegName, Point]) -> Trajectories:
        """
        Generates trajectories points for visual representation.
        """

        timestep = self.gait_planner.period / 100
        gait_times = np.arange(0, self.gait_planner.period, timestep)

        trajectories: Trajectories = []
        for leg_name in LegName:
            trajectory: Trajectory = []

            # Generate points.
            for gait_time in gait_times:
                phase, phase_time = self.gait_planner.get_leg_phase_time(leg_name, gait_time)
                d, h = self.gait_planner.foot_trajectory_bezier(phase, phase_time, stride_length=0.15)
                t_point = Point(d, 0, h)

                # Move point foot location.
                foot_position = base_foot_points[leg_name]
                t_point.move_xyz(foot_position.x, foot_position.y, foot_position.z)

                trajectory.append(t_point)

            trajectories.append(trajectory)
        return trajectories

    ###############################################################################
    ###############################################################################
