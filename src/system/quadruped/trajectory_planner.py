import numpy as np
from numpy.typing import NDArray
from math import radians, floor
from typing import List, TypeAlias
from math import sqrt, log, copysign
from enum import Enum

from system.quadruped.parameters.motion_parameters import MotionParameters
from system.quadruped.quad import Quad
from system.quadruped.leg import Leg
from system.quadruped.point import (
    Point,
    rotz,
    get_distance_xy,
    angle_between_xy,
    get_distance_statistics,
)
from system.quadruped.bezier import generate_bezier_points

"""
    A trajectory is a series of points representing foot positions from where the inverse kinematics will be calculated.
    The points create rotation and walking gaits.

    Trajectory requirements:        
        Trajectories at index 0 is expected to start at the neutral foot position.
        Index at len(trajectory) / 2 is expected to be off the ground above the neutral foot position. 
        Even leg indexes will start on the ground, odd leg indexes will start above the ground.
        Exception is the pose and transistion trajectories.


    https://www.animatornotebook.com/learn/quadrupeds-gaits

"""

Trajectory: TypeAlias = List[Point]
Trajectories: TypeAlias = List[Trajectory]


class TransitionType(Enum):
    FULL_ARC = 0
    STRAIGHT = 1


class TrajectoryPlanner:
    def __init__(self):

        # Foot path parameters:
        self.num_points_per_bezier: int = 21  # Must be odd
        self.num_points_per_ground_stroke: int = 11  # Must be odd
        self.roll_offset: int = -4
        self.height_scale: float = 0.075
        self.length_scale: float = 0.150
        self.hard_transition_arc_height: float = 0.050

        self.rings: Trajectories = None
        self.visual_ring_num_points: int = 100

    ###############################################################################
    # Trajectory Generators
    ###############################################################################

    def generate_pose(self, quad: Quad):
        trajectories = []
        base_foot_points = quad.get_all_base_foot_points()
        for base_foot_point in base_foot_points:
            trajectories.append([base_foot_point])
        return trajectories

    def generate_rotation(self, quad: Quad):

        #radius = quad.get_centered_foot_radius()
        radius = 0.25

        #coxia_physical_directions = quad.get_all_coxia_physical_directions()

        trajectories: Trajectories = []
        for foot_index, base_foot_point in enumerate(quad.get_all_base_foot_points()):
            foot_path_points = self.generate_foot_path_points()
            self.bend_line_to_radius(points=foot_path_points, radius=radius)
            self.rotate_and_translate(
                foot_path_points,
                0,
                Point(
                    base_foot_point.x,
                    base_foot_point.y,
                    base_foot_point.z,
                ),
            )
            trajectories.append(foot_path_points)

        # self.rings = [self.create_circle_trajectory(radius, Vector(hexapod.body.cob.x, hexapod.body.cob.y, base_foot_point.z), 100)]
        self.offset_starting_indexes(trajectories, self.roll_offset)
        return trajectories

    def generate_vector_walk(self, quad: Quad, motion_parameters: MotionParameters):
        twist_angle = motion_parameters.get_heading_degrees()
        trajectories: Trajectories = []
        for foot_index, base_foot_point in enumerate(quad.get_all_base_foot_points()):
            foot_path_points = self.generate_foot_path_points()
            self.rotate_and_translate(
                foot_path_points,
                twist_angle,
                Point(base_foot_point.x, base_foot_point.y, base_foot_point.z),
            )
            trajectories.append(foot_path_points)

        self.offset_starting_indexes(trajectories, self.roll_offset)
        return trajectories

    def generate_bias_walk(self, quad: Quad, motion_parameters: MotionParameters):
        max_cor_x = 50
     
  
        base_foot_points = quad.get_all_base_foot_points()

        # Calculate the center of rotation based on the user input
        heading_raw = motion_parameters.get_heading_raw()
        center_of_rotation_x = self.log_scale_value(abs(heading_raw), 0, 1, max_cor_x, 0)
        if heading_raw < 0.0:
            center_of_rotation_x = -center_of_rotation_x
        cor = Point(center_of_rotation_x, 0, 0)

        # The farthest foot is the upper limit of the foot path scale.
        # Either the middle right or the middle left.
        farthest_foot_index = 0 if heading_raw < 0.0 else 3
        farthest_foot_point = Point(
            base_foot_points[farthest_foot_index].x,
            base_foot_points[farthest_foot_index].y,
            base_foot_points[farthest_foot_index].z,
        )
        farthest_foot_distance = get_distance_xy(cor, farthest_foot_point)

        self.rings = []
        trajectories: Trajectories = []
        for foot_index, base_foot_point in enumerate(base_foot_points):
            # Move the foot into the centered radius due to the hexapod not being a perfect hexagon (prevent mechanical stress)
            # TODO: need to grab these values from hexapod as they currently don't take into account hip_stance
            moved_base_foot_point = Point(
                base_foot_points[foot_index].x,
                base_foot_points[foot_index].y,
                base_foot_points[foot_index].z,
                base_foot_point.z,
            )

            # Get the radius from the center-of-rotation to the foot
            bend_radius = get_distance_xy(cor, moved_base_foot_point)
            if copysign(1, center_of_rotation_x) == 1.0:
                bend_radius *= -1

            # The length of the foot path gets smaller the closer the center of rotation is the foot.
            length_scale = self.scale_value(abs(bend_radius), 0, farthest_foot_distance, 0, self.length_scale)

            foot_path_points = self.generate_foot_path_points(length_scale=length_scale)
            self.bend_line_to_radius(points=foot_path_points, radius=bend_radius)

            # Find the twist angle so the foot points are tangent to the center of rotation
            twist_angle = angle_between_xy(cor, moved_base_foot_point)
            if copysign(1, center_of_rotation_x) == 1.0:
                twist_angle += 180

            self.rotate_and_translate(
                foot_path_points,
                twist_angle,
                Point(
                    base_foot_points[foot_index].x,
                    base_foot_points[foot_index].y,
                    base_foot_points[foot_index].z,
                    base_foot_point.z,
                ),
            )

            trajectories.append(foot_path_points)
            self.rings.append(
                self.create_circle_trajectory(
                    bend_radius,
                    Point(cor.x, cor.y, base_foot_point.z),
                    self.visual_ring_num_points,
                )
            )

        self.offset_starting_indexes(trajectories, self.roll_offset)
        return trajectories

    def generate_transition(
        self,
        quad: Quad,
        target_foot_points: List[Point],
        transition_type: TransitionType,
    ):
        trajectories: Trajectories = []
        foot_points = quad.get_all_foot_points()
        base_foot_points = quad.get_all_base_foot_points()

        for foot_index in range(len(foot_points)):
            foot_point = foot_points[foot_index]
            base_foot_point = base_foot_points[foot_index]
            target_foot_point = target_foot_points[foot_index]

            # Create a straight line straight down that touches the ground
            num_points_touchdown = int(self.num_points_per_bezier / 2)
            x_touchdown = np.tile(foot_point.x, num_points_touchdown)
            y_touchdown = np.tile(foot_point.y, num_points_touchdown)
            z_touchdown = np.linspace(foot_point.z, base_foot_point.z, num_points_touchdown + 1)

            # Create an arc that lifts foot off the ground and back down
            num_points_arc = self.num_points_per_bezier
            x_arc_to_target = np.linspace(foot_point.x, target_foot_point.x, num_points_arc)
            y_arc_to_target = np.linspace(foot_point.y, target_foot_point.y, num_points_arc)
            half_arc_linespace = np.linspace(0, np.pi / 2, int(num_points_arc / 2))
            full_arc_linespace = np.concatenate((half_arc_linespace, half_arc_linespace[::-1]))
            z_arc_to_target = target_foot_point.z + self.hard_transition_arc_height * np.sin(full_arc_linespace)

            # Create points that hold current ground position
            x_hold_target_foot = np.tile(target_foot_point.x, num_points_arc)
            y_hold_target_foot = np.tile(target_foot_point.y, num_points_arc)
            z_hold_target_foot = np.tile(target_foot_point.z, num_points_arc)

            x_hold_foot = np.tile(foot_point.x, num_points_arc)
            y_hold_foot = np.tile(foot_point.y, num_points_arc)
            z_hold_foot = np.tile(base_foot_point.z, num_points_arc)

            # Create points that move straight to the target position
            x_straight = np.linspace(x_hold_foot[-1], target_foot_point.x, num_points_arc)
            y_straight = np.linspace(y_hold_foot[-1], target_foot_point.y, num_points_arc)
            z_straight = np.linspace(z_hold_foot[-1], target_foot_point.z, num_points_arc)

            # Choose which pattern to apply
            if foot_index % 2 == 1:
                x = np.concatenate((x_touchdown, x_arc_to_target[1:-1], x_hold_target_foot[1:-1]))
                y = np.concatenate((y_touchdown, y_arc_to_target[1:-1], y_hold_target_foot[1:-1]))
                z = np.concatenate((z_touchdown, z_arc_to_target[1:-1], z_hold_target_foot[1:-1]))
            else:
                if transition_type == TransitionType.FULL_ARC:
                    x = np.concatenate((x_touchdown, x_hold_foot[1:-1], x_arc_to_target[1:-1]))
                    y = np.concatenate((y_touchdown, y_hold_foot[1:-1], y_arc_to_target[1:-1]))
                    z = np.concatenate((z_touchdown, z_hold_foot[1:-1], z_arc_to_target[1:-1]))
                elif transition_type == TransitionType.STRAIGHT:
                    x = np.concatenate((x_touchdown, x_hold_foot[1:-1], x_straight[1:-1]))
                    y = np.concatenate((y_touchdown, y_hold_foot[1:-1], y_straight[1:-1]))
                    z = np.concatenate((z_touchdown, z_hold_foot[1:-1], z_straight[1:-1]))
            trajectories.append([Point(xi, yi, zi) for xi, yi, zi in zip(x, y, z)])

        return trajectories

    def generate_soft_transition(self, quad: Quad, target_trajectories: Trajectories, target_foot_points: List[Point]) -> Trajectories:
        """
        Trajectory lengths may not be equal, but must at least a length of one.
        """

        trajectories: Trajectories = []
        foot_points = quad.get_all_foot_points()
        ground_indexes, air_indexes = quad.get_tripod_ground_contact_indexes()

        # TODO: test target foot point being the closest point in the target trajectory
        # TODO: test if air point is barely off the ground, if so then raise it ~25mm

        max_num_points: int = 0
        for foot_index in air_indexes:
            foot_to_foot_distance = get_distance_xy(foot_points[foot_index], target_foot_points[foot_index])
            min_dist, avg_dist, max_dist = get_distance_statistics(target_trajectories[foot_index])
            num_points = int(round(foot_to_foot_distance / avg_dist))
            max_num_points = max(max_num_points, num_points)

        for foot_index in range(len(foot_points)):
            foot_point = foot_points[foot_index]
            target_foot_point = target_foot_points[foot_index]

            if foot_index in ground_indexes:
                x = [foot_point.x]
                y = [foot_point.y]
                z = [foot_point.z]
            elif foot_index in air_indexes:
                if max_num_points == 0:
                    x = [foot_point.x]
                    y = [foot_point.y]
                    z = [foot_point.z]
                else:
                    # Create points that move straight to the target position
                    x = np.linspace(foot_point.x, target_foot_point.x, max_num_points)
                    y = np.linspace(foot_point.y, target_foot_point.y, max_num_points)
                    z = np.linspace(foot_point.z, target_foot_point.z, max_num_points)

            trajectories.append([Vector(xi, yi, zi) for xi, yi, zi in zip(x, y, z)])

        return trajectories

    ###############################################################################
    # Processing Helpers
    ###############################################################################

    def generate_foot_path_points(self, num_points=None, length_scale=None, height_scale=None) -> Trajectory:
        """
        Generates foot path using bezier curves.
        """

        # Add two extra points to the beizer curve which be removed in the next step
        beizer_points = generate_bezier_points(
            num_points=num_points if num_points != None else self.num_points_per_bezier + 2,
            length_scale=length_scale if length_scale != None else self.length_scale,
            height_scale=height_scale if height_scale != None else self.height_scale,
        )

        linspace = np.linspace(beizer_points[-1].y, beizer_points[0].y, int(self.num_points_per_ground_stroke))
        ground_start_points = [Point(0, value, 0) for value in linspace][1:-1]

        return ground_start_points + beizer_points

    def rotate_and_translate(self, points: np.ndarray, twist_angle: float, vector: Point):
        """
        Rotates and translates an array of Points.
        """
        twist_frame = rotz(twist_angle)
        for index in range(len(points)):
            points[index].update_point_wrt_frame(twist_frame)
            points[index].move_xyz(
                vector.x,
                vector.y,
                vector.z,
            )

    def offset_starting_indexes(self, trajectories: Trajectory, offset: int = 0):
        """
        Apply an offset so every other leg starts in the middle of the path thats creates a tripod gait.
        """
        for index in range(len(trajectories)):
            if index % 2 == 0:
                roll = int(len(trajectories[index]) / 2) + offset
            else:
                roll = offset
            trajectories[index] = trajectories[index][-roll:] + trajectories[index][:-roll]

    ###############################################################################
    # Getters / Setters
    ###############################################################################

    def get_rings(self) -> Trajectories:
        return self.rings

    ###############################################################################
    # Helpers
    ###############################################################################

    @staticmethod
    def scale_value(value, old_min, old_max, new_min, new_max):
        if old_max == old_min:
            raise ValueError("old_max and old_min cannot be the same value.")
        return (value - old_min) / (old_max - old_min) * (new_max - new_min) + new_min

    @staticmethod
    def log_scale_value(value, old_min, old_max, new_min, new_max):
        if old_max == old_min:
            raise ValueError("old_max and old_min cannot be the same value.")
        if value <= 0:
            return new_min

        if old_min <= 0:
            log_old_min = log(old_min + 0.000001)
        else:
            log_old_min = log(old_min)

        log_old_max = log(old_max)
        log_value = log(value)

        return (log_value - log_old_min) / (log_old_max - log_old_min) * (new_max - new_min) + new_min

    @staticmethod
    # https://math.stackexchange.com/questions/1391470/find-distance-between-point-on-tangent-line-and-circle
    def bend_line_to_radius(points: List[Point], radius: float):
        """
        Bends a line along the y axis to a given radius.
        """
        for point in points:
            a = point.y * 2

            if (radius * radius) - (a * a) / 4 < 0:
                return

            distance_from_circle = abs(radius) - sqrt((abs(radius) * abs(radius)) - (a * a) / 4)

            if radius > 0:
                distance_from_circle = -distance_from_circle

            point.move_xyz(distance_from_circle, 0, 0)

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
