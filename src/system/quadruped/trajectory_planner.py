from math import radians, copysign, atan2, degrees, copysign, log1p, cos, sin
import numpy as np
from typing import Dict, Tuple
from time import sleep

from quadruped.point import Point, get_distance_xy, angle_between_xy, rotz, move_point_y_to_radius, rotate_z
from quadruped.gait_planner import GaitPlanner
from quadruped.quad import LegName
from quadruped.gait_planner import Gait, Phase, SwingPattern
from quadruped.interfaces import Trajectories, Trajectory
from utilities.utilities import log_scale_value, scale_value


class TrajectoryPlanner:

    def __init__(self):
        self.gait_planner: GaitPlanner = self.gait_factory(Gait.CRAWL)

        self.trajectory_num_points: int = 40
        self.ring_num_points: int = 40

    ###############################################################################
    # Gaits (can be modified)
    ###############################################################################

    def gait_factory(self, gait: Gait) -> GaitPlanner:
        if gait == Gait.CRAWL:
            return GaitPlanner(
                gait=Gait.CRAWL,
                swing_pattern=SwingPattern.BEZIER_ARC,
                period=1.0,
                duty_factor=0.75,
                stride_length=0.1,
                step_height=0.02,
                phase_offsets={
                    LegName.FR: 0.0,
                    LegName.BL: 0.25,
                    LegName.FL: 0.5,
                    LegName.BR: 0.75,
                },
            )
        elif gait == Gait.RUN:
            return GaitPlanner(
                gait=Gait.RUN,
                swing_pattern=SwingPattern.BEZIER_ARC,
                period=1.0,
                duty_factor=0.5,
                stride_length=0.10,
                step_height=0.06,
                phase_offsets={
                    LegName.FR: 0.0,
                    LegName.BL: 0.0,
                    LegName.FL: 0.5,
                    LegName.BR: 0.5,
                },
            )
        elif gait == Gait.TROT:
            return GaitPlanner(
                gait=Gait.TROT,
                swing_pattern=SwingPattern.BEZIER_ARC,
                period=1.0,
                duty_factor=0.5,
                stride_length=0.10,
                step_height=0.02,
                phase_offsets={
                    LegName.FR: 0.0,
                    LegName.BL: 0.0,
                    LegName.FL: 0.5,
                    LegName.BR: 0.5,
                },
            )

    ###############################################################################
    # Methods
    ###############################################################################
   

    def _calculate_foot_point(
        self, gait_planner: GaitPlanner, leg_name: LegName, base_foot_point: Point, gait_time: float, forward_velocity: float, lateral_velocity: float, angular_velocity: float
    ):
        """
        Calculate a leg's foot position given the gait_time and heading.
        """
             
        max_cor = 10
        heading = (degrees(atan2(-lateral_velocity, forward_velocity))) % 360
        stride_length_scale = abs(max(forward_velocity, lateral_velocity, angular_velocity, key=abs)) if gait_planner.gait is Gait.RUN else 1
    

        if angular_velocity == 0:   
            foot_point = gait_planner.get_foot_position(leg_name, gait_time, stride_length_scale)       
            foot_point.update_point_wrt_frame(rotz(heading))          
            foot_point.move_xyz(base_foot_point.x, base_foot_point.y, base_foot_point.z)
            return foot_point, heading, max_cor, Point(0,0,0)
                  
        cor = Point(0, -forward_velocity/angular_velocity, 0)  
        cor = rotate_z(cor, heading)

        # Get the radius from CoR to the leg's nominal foot position
        bend_radius = get_distance_xy(cor, base_foot_point)

        twist_angle = angle_between_xy(cor, base_foot_point)

        # Compenstate for quadrant shifts.
        if forward_velocity < 0:
            twist_angle -= 180
            bend_radius *= -1
        elif forward_velocity > 0:
            pass
        elif forward_velocity == 0:
            pass

        if lateral_velocity < 0:
            twist_angle -= 180
        elif lateral_velocity > 0:
            twist_angle += 180
        elif lateral_velocity == 0:
            twist_angle += 180

        if angular_velocity < 0:
            twist_angle -= 90
            bend_radius *= -1
        elif angular_velocity > 0:
            twist_angle += 90
        elif angular_velocity == 0:
            twist_angle += 90
     
        # Foot swing trajectory along the x (unrotated, origin-relative)        
        foot_point = gait_planner.get_foot_position(leg_name, gait_time, stride_length_scale)
              
        # Project the foot point to the bend radius.
        move_point_y_to_radius(foot_point, bend_radius)

        # Rotate foot point to match the twist.
        foot_point.update_point_wrt_frame(rotz(twist_angle))

        # Translate foot point into the base foot reference frame.
        foot_point.move_xyz(base_foot_point.x, base_foot_point.y, base_foot_point.z)

        return foot_point, twist_angle, bend_radius, cor

    def get_foot_points(
        self, base_foot_points: Dict[LegName, Point], gait_time: float, forward_velocity: float, lateral_velocity: float, angular_velocity: float
    ) -> Dict[LegName, Point]:
        foot_points: Dict[LegName, Point] = {}
        for leg in LegName:
            base_foot_point = base_foot_points[leg]
            foot_point, _, _, _ = self._calculate_foot_point(self.gait_planner, leg, base_foot_point, gait_time, forward_velocity, lateral_velocity, angular_velocity)
            foot_points[leg] = foot_point
        return foot_points

    def is_leg_in_swing(self, leg: LegName, phase_time: float):
        phase, normalized_time = self.gait_planner.get_leg_phase_time(leg, phase_time)
        return phase is Phase.SWING

    def get_twist_angle(
        self,
        base_foot_points: Dict[LegName, Point],
        leg_name: LegName,
        gait_time: float,
        forward_velocity: float,
        lateral_velocity: float,
        angular_velocity: float,
    ) -> float:
        base_foot_point = base_foot_points[leg_name]
        _, twist_angle, _, _ = self._calculate_foot_point(self.gait_planner, leg_name, base_foot_point, gait_time, forward_velocity, lateral_velocity,angular_velocity)
        return twist_angle

    ###############################################################################
    # Visualizations
    ###############################################################################

    def get_trajectories(
        self, base_foot_points: Dict[LegName, Point], forward_velocity: float, lateral_velocity: float, angular_velocity: float
    ) -> Tuple[Trajectories, Trajectories, Trajectories]:
        """
        Generates trajectories points for visual representation.
        """

        bend_radius: float = None
        cor: Point = None

        timestep = self.gait_planner.period / self.trajectory_num_points
        gait_times = np.arange(0, self.gait_planner.period, timestep)

        trajectories: Trajectories = []
        rings: Trajectories = []
        for leg_name in LegName:
            base_foot_point = base_foot_points[leg_name]

            trajectory: Trajectory = []
            for gait_time in gait_times:
                foot_point, _, bend_radius, cor = self._calculate_foot_point(self.gait_planner, leg_name, base_foot_point, gait_time, forward_velocity, lateral_velocity, angular_velocity)
                trajectory.append(foot_point)
                sleep(0)  # Yeild CPU frequently to prevent other thread slow downs.
            trajectories.append(trajectory)

            # if leg_name is LegName.FL or leg_name is LegName.FR:
            rings.append(self.create_circle_trajectory(bend_radius, cor, self.ring_num_points))

        return trajectories, rings

    @staticmethod
    def create_circle_trajectory(radius: float, center: Point, num_points: int) -> Trajectory:
        angles = np.linspace(0, 2 * np.pi, num_points)
        sin_vals = np.sin(angles)
        cos_vals = np.cos(angles)

        # Precompute coordinates
        x = radius * sin_vals + center.x
        y = radius * cos_vals + center.y
        z = np.full(num_points, center.z)

        # Construct trajectory
        trajectory = [Point(float(x[i]), float(y[i]), float(z[i])) for i in range(num_points)]
        return trajectory

    ###############################################################################
    # Getters / Setters
    ###############################################################################


    @property
    def gait(self) -> Gait:
        return self.gait_planner.gait

    @gait.setter
    def gait(self, gait: Gait):
        self.gait_planner = self.gait_factory(gait)
