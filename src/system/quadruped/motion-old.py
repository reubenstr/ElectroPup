from time import time
from typing import List

from system.quadruped.trajectory_planner import TrajectoryPlanner, TransitionType
from system.quadruped.point import Point, add_vectors, get_distance_xy, get_distance_statistics
from system.quadruped.quad import Quad
from system.quadruped.parameters.ik_parameters import IKParameters
from system.quadruped.parameters.motion_parameters import MotionParameters
from system.interfaces import MotionState, Gaits
from system.utilities.utilities import safe_divide, scale_value
from system.quadruped.trajectory_planner import Trajectory, Trajectories

"""
    Generates trajectories for walking and rotation.
    Trajectories are a series of foot positions.
"""


class Motion:
    def __init__(self):
        self.tick_rate_max_hz: float = 20
        self.tick_rate_min_hz: float = 0
        self.tick_start_time: float = 0

        # TODO: only tripod gait currently supported by the TrajectoryPlanner
        self.gait = Gaits.TRIPOD

        self.idle_user_input_timeout_seconds: float = 3
        self.last_user_input_time: float = time()

        self.trajectories: Trajectories = []
        self.trajectory_index = 0
        self.soft_transition_flag: bool = False
        self.soft_trajectory_index: int = 0
        self.soft_trajectories: Trajectories = []

        self.motion_state = MotionState.BIAS_WALK
        self.target_motion_state: MotionState = MotionState.VECTOR_WALK
        self.previous_motion_state = None

        self.trajectory_planner = TrajectoryPlanner()

    ###############################################################################
    # Tick : Execute every main loop
    ###############################################################################

    def tick(
        self,
        quad: Quad,
        ik_parameters: IKParameters,
        motion_parameters: MotionParameters,
    ):
        # TODO: check for user idle

        self.process_trajectory_state(quad, ik_parameters, motion_parameters)

        current_foot_points = quad.get_all_foot_points()
        target_foot_points: List[Point] = [self.trajectories[i][self.trajectory_index] for i in range(quad.get_num_legs())]

        # for i in range(quad.get_num_legs()):
        #    quad.set_foot_point_by_leg_index(i, target_foot_points[i])

        if self.motion_state != MotionState.POSE:
            ik_parameters = IKParameters()

        # quad.set_body_pose_by_transform_inputs(ik_parameters)

        self.increment_trajectory_index(motion_parameters)

    ###############################################################################
    # Methods
    ###############################################################################

    def increment_trajectory_index(self, motion_parameters: MotionParameters):
        if time() - self.tick_start_time > self.calculate_tick_delay(motion_parameters):
            self.tick_start_time = time()

            direction = 1 if motion_parameters.get_forward_direction() == True else -1
            direction = 1 if self.motion_state == MotionState.TRANSITION else direction

            if self.soft_transition_flag:
                self.soft_trajectory_index = self.soft_trajectory_index + 1
            else:
                self.trajectory_index = (self.trajectory_index + direction) % len(self.trajectories[0])
                if self.trajectory_index == 0:
                    self.process_end_of_trajectory()

    def calculate_tick_delay(self, motion_parameters: MotionParameters) -> float:
        """
        Determines walking speed by calculating tick delay in hz then converting into seconds.
        """
        if self.motion_state == MotionState.TRANSITION:
            tick_rate_hz = self.tick_rate_max_hz
        else:
            tick_rate_hz = scale_value(
                abs(motion_parameters.get_forward_raw()),
                0,
                1,
                self.tick_rate_min_hz,
                self.tick_rate_max_hz,
            )
        return safe_divide(1, tick_rate_hz)

    def process_end_of_trajectory(self):
        if self.motion_state == MotionState.TRANSITION:
            self.motion_state = self.target_motion_state

    def process_trajectory_state(
        self,
        quad: Quad,
        ik_parameters: IKParameters,
        motion_parameters: MotionParameters,
    ):

        # Target motion state has changed, start transition
        if self.motion_state != self.target_motion_state:
            self.motion_state = MotionState.TRANSITION

        # Process only when state changes:
        if self.previous_motion_state != self.motion_state:
            self.previous_motion_state = self.motion_state

            self.trajectory_index = 0
            self.trajectories = self.generate_trajectory(quad, motion_parameters, self.motion_state)

        # Process every loop:
        if self.motion_state in [MotionState.VECTOR_WALK, MotionState.BIAS_WALK]:
            self.trajectories = self.generate_trajectory(quad, motion_parameters, self.motion_state)

    def generate_trajectory(
        self,
        quad: Quad,
        motion_parameters: MotionParameters,
        motion_state: MotionState,
    ) -> Trajectories:

        if motion_state == MotionState.TRANSITION:
            if self.target_motion_state in [
                MotionState.ROTATE,
                MotionState.VECTOR_WALK,
                MotionState.BIAS_WALK,
            ]:
                transition_type = TransitionType.STRAIGHT
            elif self.target_motion_state == MotionState.POSE:
                transition_type = TransitionType.FULL_ARC

            temp_trajectories = self.generate_trajectory(quad, motion_parameters, self.target_motion_state)
            target_foot_points = [trajectory[0] for trajectory in temp_trajectories]
            trajectories = self.trajectory_planner.generate_transition(quad, target_foot_points, transition_type)

        elif motion_state == MotionState.POSE:
            trajectories = self.trajectory_planner.generate_pose(quad)

        elif motion_state == MotionState.ROTATE:
            trajectories = self.trajectory_planner.generate_rotation(quad)

        elif motion_state == MotionState.VECTOR_WALK:
            trajectories = self.trajectory_planner.generate_vector_walk(quad, motion_parameters)

        elif motion_state == MotionState.BIAS_WALK:
            trajectories = self.trajectory_planner.generate_bias_walk(quad, motion_parameters)

        return trajectories

    ###############################################################################
    # Getters / Setters
    ###############################################################################

    def get_trajectories(self) -> Trajectories:
        return self.trajectories

    def get_soft_trajectories(self) -> Trajectories:
        if self.soft_transition_flag:
            return self.soft_trajectories
        return []

    def get_motion_state(self) -> MotionState:
        return self.motion_state

    def get_target_motion_state(self) -> MotionState:
        return self.target_motion_state

    def get_visual_rings(self) -> Trajectories:
        if self.motion_state == MotionState.BIAS_WALK:
            return self.trajectory_planner.get_rings()
        else:
            return None

    def set_target_motion_state(self, state: MotionState):
        self.target_motion_state = state

    def is_in_motion(self) -> bool:
        return self.motion_state != MotionState.POSE

    def get_gait(self) -> Gaits:
        return self.gait
