from math import radians, copysign
import numpy as np
from typing import Dict, Tuple

from system.quadruped.point import Point, get_distance_xy, angle_between_xy, rotz, move_point_y_to_radius
from system.quadruped.gait_planner import GaitPlanner
from system.quadruped.quad import LegName
from system.quadruped.gait_planner import Gait, Phase
from system.quadruped.interfaces import Trajectories, Trajectory
from system.utilities.utilities import log_scale_value


class TrajectoryPlanner:

    ###############################################################################
    # Gaits (can be modified)
    ###############################################################################

    def gait_factory(self, gait: Gait) -> GaitPlanner:
        if gait == Gait.WALK:
            return GaitPlanner(
                gait=Gait.WALK,
                period=1.0,
                duty_factor=0.75,
                stride_length=0.075,
                step_height=0.05,
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
                stride_length=0.075,
                step_height=0.05,
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

    def _calculate_foot_point(self, gait: Gait, leg_name: LegName, base_foot_point: Point, gait_time: float, angular_velocity: float, forward_velocity: float):
        """
        Calculate a leg's foot position given the gait_time and heading.
        """

        deadzone = 0.05
        max_cor = 100

        # Calculate CoR (center-of-rotation)
        if abs(forward_velocity) < deadzone and abs(angular_velocity) < deadzone:
            # Standing still
            #turning_radius = max_cor
            cor = Point(0, max_cor, 0)
        elif abs(forward_velocity) >= deadzone and abs(angular_velocity) < deadzone:
            # Straight walking
            #urning_radius = max_cor
            cor = Point(0, max_cor, 0)
        elif abs(forward_velocity) < deadzone and abs(angular_velocity) >= deadzone:
            # In-place rotation
            #turning_radius = 0.0
            cor = Point(0, 0, 0)
        else:
            # Curved walking
            #turning_radius = (forward_velocity / angular_velocity) / 5
            cor = Point(0, (forward_velocity / angular_velocity) / 5, 0)

        # Get the radius from CoR to the leg's nominal foot position
        bend_radius = get_distance_xy(cor, base_foot_point)
        if cor.y > 0:
            bend_radius *= -1

        # Angle from CoR to the foot, then apply tangent direction
        twist_angle = angle_between_xy(cor, base_foot_point)
        twist_angle += 90 if cor.y > 0 else -90

        # Foot swing trajectory (unrotated, origin-relative)
        gait_planner: GaitPlanner = self.gait_factory(gait)
        foot_point: Point = gait_planner.get_foot_position(leg_name, gait_time)

        # Project it to the circular arc radius
        move_point_y_to_radius(foot_point, bend_radius)

        # Rotate to match circular motion tangent
        foot_point.update_point_wrt_frame(rotz(twist_angle))

        # Translate into the foot's actual reference frame
        foot_point.move_xyz(base_foot_point.x, base_foot_point.y, base_foot_point.z)

        return foot_point, twist_angle, bend_radius, cor

    def get_foot_points(
        self, gait: Gait, base_foot_points: Dict[LegName, Point], gait_time: float, angular_velocity: float, forward_velocity: float
    ) -> Dict[LegName, Point]:
        foot_points: Dict[LegName, Point] = {}
        for leg_name in LegName:
            base_foot_point = base_foot_points[leg_name]
            foot_point, _, _, _ = self._calculate_foot_point(gait, leg_name, base_foot_point, gait_time, angular_velocity, forward_velocity)
            foot_points[leg_name] = foot_point
        return foot_points

    def is_leg_in_swing(self, gait: Gait, leg: LegName, phase_time: float):
        gait_planner: GaitPlanner = self.gait_factory(gait)
        phase, normalized_time = gait_planner.get_leg_phase_time(leg, phase_time)
        return phase is Phase.SWING
    
    def get_twist_angle(self, gait: Gait, base_foot_points: Dict[LegName, Point], leg_name: LegName, gait_time: float, angular_velocity: float, forward_velocity: float) -> float:
        base_foot_point = base_foot_points[leg_name]
        _, twist_angle, _, _ = self._calculate_foot_point(gait, leg_name, base_foot_point, gait_time, angular_velocity, forward_velocity)
        return twist_angle

    ###############################################################################
    # Visualizations
    ###############################################################################

    def get_trajectories(
        self, gait: Gait, base_foot_points: Dict[LegName, Point], angular_velocity: float, forward_velocity
    ) -> Tuple[Trajectories, Trajectories, Trajectories]:
        """
        Generates trajectories points for visual representation.
        """

        gait_planner: GaitPlanner = self.gait_factory(gait)

        timestep = gait_planner.period / 100
        gait_times = np.arange(0, gait_planner.period, timestep)

        trajectories: Trajectories = []
        rings: Trajectories = []
        for leg_name in LegName:
            base_foot_point = base_foot_points[leg_name]

            trajectory: Trajectory = []
            for gait_time in gait_times:
                foot_point, _, bend_radius, cor = self._calculate_foot_point(gait, leg_name, base_foot_point, gait_time, angular_velocity, forward_velocity)
                trajectory.append(foot_point)

            trajectories.append(trajectory)
            rings.append(self.create_circle_trajectory(bend_radius, cor, 100))

        return trajectories, rings

    @staticmethod
    def create_circle_trajectory(radius: float, center: Point, num_points: int) -> Trajectory:
        """Creates a circle trajectory"""
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
