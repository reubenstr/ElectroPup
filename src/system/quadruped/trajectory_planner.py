from enum import Enum
from time import time, sleep
from math import radians, degrees, copysign, log, sqrt, cos, sin
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, TypeAlias

from system.quadruped.point import Point, get_distance_xy, angle_between_xy, rotz, move_point_y_to_radius
from system.quadruped.quad import Quad
from system.quadruped.gait import GaitPlanner
from system.interfaces import LegName
from system.quadruped.gait import Gait
from system.utilities.utilities import log_scale_value

Trajectory: TypeAlias = List[Point]
Trajectories: TypeAlias = List[Trajectory]


class TrajectoryPlanner:
    def __init__(self):

        self.set_gait(Gait.WALK)
        self.gait_time: float = 0.0

        self.visual_rings: Trajectories = None

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
   
    def get_foot_point(self, leg_name: LegName, base_foot_point: Point, heading: float):
        phase, phase_time = self.gait_planner.get_leg_phase_time(leg_name, self.gait_time)
        d, h = self.gait_planner.foot_trajectory_bezier(phase, phase_time, stride_length=0.15)
        point = Point(d, 0, h)

        # Move point foot location.
        point.move_xyz(base_foot_point.x, base_foot_point.y, base_foot_point.z)

       
        #point.x = cos(heading) * point.x - sin(heading) * point.y
        #point.y = sin(heading) * point.x + cos(heading) * point.y

      

        # Bend point to rotation circle

        # Calculate the center of rotation based on the user input
        max_cor_x = 50
        cor_offset = log_scale_value(abs(heading), 0, 1, max_cor_x, 0)
        if heading < 0.0:
            cor_offset = -cor_offset
        cor = Point(0, cor_offset, 0)

        # Get the radius from the center-of-rotation to the foot
        bend_radius = get_distance_xy(cor, base_foot_point)
        if copysign(1, cor_offset) == 1.0:
            bend_radius *= -1

        #self.bend_point_to_radius(point, bend_radius)



        # The length of the foot path gets smaller the closer the center of rotation is the foot.
        '''self.length_scale: float = 0.150
        length_scale = self.scale_value(abs(bend_radius), 0, bend_radius, 0, self.length_scale)

        foot_path_points = self.generate_foot_path_points(length_scale=length_scale)
        self.bend_line_to_radius(points=foot_path_points, radius=bend_radius)'''

        


        return point

    def get_trajectories(self, base_foot_points: Dict[LegName, Point], heading: float) -> Trajectories:
        """
        Generates trajectories points for visual representation.
        """

        timestep = self.gait_planner.period / 100
        gait_times = np.arange(0, self.gait_planner.period, timestep)

        trajectories: Trajectories = []
        visual_rings: Trajectories = []
        for leg_name in LegName:

            trajectory: Trajectory = []
            visual_ring: Trajectory = []

            foot_position = base_foot_points[leg_name]

            # Create a center-of-rotation given the heading input.
            max_cor_x = 50
            cor_offset = log_scale_value(abs(heading), 0, 1, max_cor_x, 0)
            if heading < 0.0:
                cor_offset = -cor_offset
            cor = Point(0, cor_offset, 0)

            # Get the radius from the center-of-rotation to the foot
            bend_radius = get_distance_xy(cor, foot_position)
            if copysign(1, cor_offset) > 0:
                bend_radius *= -1
                                                   
            # Find the twist angle so the foot points are tangent to the center of rotation
            twist_angle = angle_between_xy(cor, foot_position)            
            if copysign(1, cor_offset) > 0:
                twist_angle += 90
            else:
                twist_angle -= 90
            
            # Generate points.
            for gait_time in gait_times:
                phase, phase_time = self.gait_planner.get_leg_phase_time(leg_name, gait_time)
                d, h = self.gait_planner.foot_trajectory_bezier(phase, phase_time, stride_length=0.075)
                t_point = Point(d, 0, h)
                    
                # Move the point to match the rotation radius.
                move_point_y_to_radius(t_point, bend_radius) 
                
                # Rotate the point to be tangent to the rotation radius.
                t_point.update_point_wrt_frame(rotz(twist_angle))

                # Move the point to match the foot position.
                t_point.move_xyz(foot_position.x,foot_position.y,foot_position.z)
               
                trajectory.append(t_point)
            
            trajectories.append(trajectory)
            visual_rings.append(self.create_circle_trajectory(bend_radius, cor, 100))

        self.visual_rings = visual_rings  
        return trajectories

    
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
    


    ###############################################################################
    # Getters / Setters
    ###############################################################################

    def get_visual_rings(self) -> Trajectories:
        return self.visual_rings
    
    ###############################################################################
    # Helpers
    ###############################################################################
      
    @staticmethod
    def move_point_to_radius(point: Point, radius: float):
        """
        Moves a point along the x axis to a given radius.
        """
       
        a = point.x * 2

        if (radius * radius) - (a * a) / 4 < 0:
            return

        distance_from_circle = abs(radius) - sqrt((abs(radius) * abs(radius)) - (a * a) / 4)

        if radius > 0:
            distance_from_circle = -distance_from_circle

        point.move_xyz(0, distance_from_circle, 0)

