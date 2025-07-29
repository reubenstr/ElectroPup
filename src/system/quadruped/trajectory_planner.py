from math import radians, copysign
import numpy as np
from typing import List, Dict, TypeAlias, Tuple

from system.quadruped.point import Point, get_distance_xy, angle_between_xy, rotz, move_point_y_to_radius
from system.quadruped.gait_planner import GaitPlanner
from system.quadruped.quad import LegName
from system.quadruped.gait_planner import Gait
from system.utilities.utilities import log_scale_value

Trajectory: TypeAlias = List[Point]
Trajectories: TypeAlias = List[Trajectory]


class TrajectoryPlanner:
    def __init__(self):
        pass
      
    ###############################################################################
    # Gaits (can be modified)
    ###############################################################################
        
    def gait_factory(self, gait: Gait) -> GaitPlanner:
        if gait == Gait.WALK:
            return GaitPlanner(
                gait=Gait.WALK,
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
                gait=Gait.TROT,
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

    def get_foot_point(self, gait: Gait, leg_name: LegName, base_foot_point: Point, gait_time: float, heading: float):
        foot_point, bend_radius, cor = self.calc(gait, leg_name, base_foot_point, gait_time, heading)
        return foot_point

    def calc(self, gait: Gait,  leg_name: LegName, base_foot_point: Point, gait_time: float, heading: float):
        """
        Calculate a leg's foot position given the gait_time and heading.
        """

        gait_planner: GaitPlanner = self.gait_factory(gait)

        # Create a center-of-rotation given the heading input.
        max_cor_x = 50
        cor_offset = log_scale_value(abs(heading), 0, 1, max_cor_x, 0)
        if heading < 0.0:
            cor_offset = -cor_offset
        cor = Point(0, cor_offset, 0)

        # Get the radius (distance) from the center-of-rotation to the foot.
        bend_radius = get_distance_xy(cor, base_foot_point)
        if copysign(1, cor_offset) > 0:
            bend_radius *= -1

        # Find the twist angle required to rotate the foot points tangent to the center of rotation.
        twist_angle = angle_between_xy(cor, base_foot_point)
        if copysign(1, cor_offset) > 0:
            twist_angle += 90
        else:
            twist_angle -= 90

        # Get phase and phase time of the leg.
        phase, phase_time = gait_planner.get_leg_phase_time(leg_name, gait_time)

        # Generate foot offsets given the phase and phase time.
        d, h = gait_planner.foot_trajectory_bezier(phase, phase_time, stride_length=0.075)
        foot_point = Point(d, 0, h)

        # Move the point to match the rotation radius (projects path along the y)
        move_point_y_to_radius(foot_point, bend_radius)

        # Rotate the point to be tangent to the rotation radius.
        foot_point.update_point_wrt_frame(rotz(twist_angle))

        # Move the point to foot frame.
        foot_point.move_xyz(base_foot_point.x, base_foot_point.y, base_foot_point.z)

        return foot_point, bend_radius, cor

    def get_trajectories(self, gait: Gait,  base_foot_points: Dict[LegName, Point], heading: float) -> Tuple[Trajectories, Trajectories, Trajectories]:
        """
        Generates trajectories points for visual representation.
        """

        gait_planner: GaitPlanner = self.gait_factory(gait)

        timestep = gait_planner.period / 100
        gait_times = np.arange(0, gait_planner.period, timestep)

        trajectories: Trajectories = []
        visual_rings: Trajectories = []
        for leg_name in LegName:
            base_foot_point = base_foot_points[leg_name]

            trajectory: Trajectory = []
            for gait_time in gait_times:
                foot_point, bend_radius, cor = self.calc(gait, leg_name, base_foot_point, gait_time, heading)
                trajectory.append(foot_point)

            trajectories.append(trajectory)
            visual_rings.append(self.create_circle_trajectory(bend_radius, cor, 100))
            transitions = None
        
        return trajectories, visual_rings, transitions

    @staticmethod
    def create_circle_trajectory(radius: float, center: Point, num_points: int) -> Trajectory:
        """
        Creates a trajectory as a circle that used to
        validate the rotation trajectory is corectly generated.
        """
        trajectory: Trajectory = []
        linspace = np.linspace(
            radians(0),
            radians(360),
            num_points,
        )
        x = center.x + radius * np.sin(linspace)
        y = center.y + radius * np.cos(linspace)
        z = np.full_like(linspace, center.z)
        for i in range(len(x)):
            point = Point(x[i], y[i], z[i])
            trajectory.append(point)
        return trajectory
  