from time import time, sleep
from typing import List
from threading import Thread, Lock, Event
from typing import List, Dict

from system.quadruped.point import Point
from system.quadruped.quad import Quad, LegName
from system.quadruped.parameters.ik_parameters import IKParameters
from system.quadruped.parameters.motion_parameters import MotionParameters
from system.quadruped.gait_planner import Gait
from system.quadruped.trajectory_planner import TrajectoryPlanner, Trajectory, Trajectories
from system.interfaces import MotionState, Status
from system.utilities.utilities import safe_divide, scale_value


"""
    Generates trajectories for walking and rotation.
    Trajectories are a series of foot positions.
"""


class Motion:
    def __init__(self):
        self.tag = "Motion"

        self.motion_state: MotionState = MotionState.WALK
        self.target_motion_state: MotionState = MotionState.POSE
        self.gait: Gait = Gait.WALK
        self.target_gait: Gait = Gait.NONE

        self.trajectories: Trajectories = None

        self.ik_parameters = IKParameters()
        self.motion_parameters = MotionParameters()

        self.trajector_planner: TrajectoryPlanner = TrajectoryPlanner()

        self.quad = Quad()
        self.ik_status = Status.STANDBY
        self.joint_angle_status = Status.STANDBY

        self.min_loop_rate_seconds: float = 0.050
        self.loop_completion_time_ms: float = 0.0

        self.gait_time: float = 0
        self.slow_gait_time: float = 0.001
        self.fast_gait_time: float = 0.025

        self._start()

    ###############################################################################
    # Thread
    ###############################################################################

    def _start(self):
        self.lock = Lock()
        self.exit_event = Event()
        self.thread_handle = Thread(target=self._worker)
        self.thread_handle.start()

    def _stop(self):
        print(f"[{self.tag}] stoping worker thread")
        if self.thread_handle and self.thread_handle.is_alive():
            self.exit_event.set()
            self.thread_handle.join()

    def _worker(self):
        self.exit_event.clear()

        print(f"[{self.tag}] worker thread started")
        while not self.exit_event.is_set():
            loop_time = time()

            with self.lock:
                if self.motion_state == MotionState.POSE:
                    base_foot_points = self.quad.get_base_foot_points()
                    error = self.quad.set_body_pose_by_transform_inputs(self.ik_parameters, base_foot_points)
                    self._set_error(error)

                elif self.motion_state == MotionState.WALK:
                    if self.motion_parameters.forward_raw > 0:
                        dt = scale_value(self.motion_parameters.forward_raw, 0, 1, self.slow_gait_time, self.fast_gait_time)
                        self.gait_time += dt
                    elif self.motion_parameters.forward_raw < 0:
                        dt = scale_value(self.motion_parameters.forward_raw, -1, 0, -self.fast_gait_time, -self.slow_gait_time)
                        self.gait_time += dt

                    heading = self.motion_parameters.get_heading_raw()

                    foot_points: Dict[LegName, Point] = {}
                    for leg_name in LegName:
                        base_foot_point = self.quad.get_base_foot_point(leg_name)
                        foot_point = self.trajector_planner.get_foot_point(self.gait, leg_name, base_foot_point, self.gait_time, heading)
                        foot_points[leg_name] = foot_point

                    error = self.quad.set_body_pose_by_transform_inputs(IKParameters(), foot_points)
                    self._set_error(error)

            delta = time() - loop_time

            if delta < self.min_loop_rate_seconds:
                sleep(self.min_loop_rate_seconds - delta)

            with self.lock:
                self.loop_completion_time_ms = (time() - loop_time) * 1000

    def _set_error(self, error: Quad.ErrorState):
        self.ik_status = Status.ERROR if error is Quad.ErrorState.KINEMATICS else Status.STANDBY
        self.joint_angle_status = Status.ERROR if error is Quad.ErrorState.JOINT else Status.STANDBY

    ###############################################################################
    # Methods
    ###############################################################################

    def generate_trajectory(
        self,
        quad: Quad,
        motion_parameters: MotionParameters,
        motion_state: MotionState,
    ):

        if motion_state == MotionState.TRANSITION:
            pass
        elif motion_state == MotionState.POSE:
            pass

        elif motion_state == MotionState.ROTATE:
            pass

        elif motion_state == MotionState.WALK:
            pass

        elif motion_state == MotionState.WALK:
            pass

    def shutdown(self):
        self._stop()

    ###############################################################################
    # Getters / Setters
    ###############################################################################

    def set_ik_parameters(self, ik_parameters: IKParameters):
        with self.lock:
            self.ik_parameters = ik_parameters

    def set_motion_parameters(self, motion_parameters: MotionParameters):
        with self.lock:
            self.motion_parameters = motion_parameters

    def set_target_motion_state(self, state: MotionState):
        with self.lock:
            self.target_motion_state = state

    def get_motion_state(self) -> MotionState:
        with self.lock:
            return self.motion_state

    def get_target_motion_state(self) -> MotionState:
        with self.lock:
            return self.target_motion_state

    def set_target_gait(self, target_gait: Gait):
        with self.lock:
            self.target_gait = target_gait

    def get_gait(self) -> Gait:
        with self.lock:
            return self.gait

    def get_target_gait(self) -> Gait:
        with self.lock:
            return self.target_gait

    def get_quad(self) -> Quad:
        with self.lock:
            return self.quad

    def get_visual_rings(self) -> Trajectories:
        with self.lock:
            if self.motion_state == MotionState.WALK:
                return self.trajector_planner.get_visual_rings()
            else:
                return None

    def get_trajectories(self) -> Trajectories:
        with self.lock:
            base_foot_points = self.quad.get_base_foot_points()
            return self.trajector_planner.get_trajectories(self.gait, base_foot_points, self.motion_parameters.heading_raw)

    def get_loop_time_ms(self) -> float:
        with self.lock:
            return self.loop_completion_time_ms

    def get_ik_status(self) -> Status:
        with self.lock:
            return self.ik_status

    def get_joint_angle_status(self) -> Status:
        with self.lock:
            return self.joint_angle_status

    ### OLD?

    def get_soft_trajectories(self) -> Trajectories:
        return
        if self.soft_transition_flag:
            return self.soft_trajectories
        return []

    def is_in_motion(self) -> bool:
        return self.motion_state != MotionState.POSE
