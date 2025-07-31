from time import time, sleep
from typing import List
from threading import Thread, Lock, Event
from typing import List, Dict, Tuple
import numpy as np

from system.quadruped.interfaces import QuadErrorState
from system.quadruped.point import Point
from system.quadruped.quad import Quad, LegName
from system.quadruped.transition_planner import TransitionPlanner
from system.quadruped.parameters.ik_parameters import IKParameters
from system.quadruped.parameters.motion_parameters import MotionParameters
from system.quadruped.gait_planner import Gait
from system.quadruped.trajectory_planner import TrajectoryPlanner, Trajectory, Trajectories
from system.interfaces import MotionState, Status
from system.utilities.utilities import safe_divide, scale_value


"""
    Applies gaits and transitions to the quadruped.
    Processes user inputs such as speed and direction.

    Notes: 
        Gait transitions are primative and should be updated for smoother transitions        
"""


class Motion:
    def __init__(self):
        self.tag = "Motion"

        self.motion_state: MotionState = MotionState.WALK
        self.target_motion_state: MotionState = MotionState.WALK
        self.previous_target_motion_state: MotionState = MotionState.WALK
        self.gait: Gait = Gait.WALK
        self.target_gait: Gait = Gait.WALK

        self.ik_parameters = IKParameters()
        self.motion_parameters = MotionParameters()

        self.quad = Quad()
        self.ik_status = Status.STANDBY
        self.joint_angle_status = Status.STANDBY
    
        self.phase_time: float = 0
        self.phase_time_rate_slow: float = 0.001
        self.phase_time_rate_fast: float = 0.025
   
        self.pose_time: float = 0
        self.pose_time_rate: float = 0.025
        self.pose_period: float = 1
    
        self.transition_time: float = 0
        self.transition_time_rate: float = 0.025

        self.idle_time: float = 0
        self.idle_time_trigger_seconds: float = 3000000
        self.idle_flag: bool = True

        self.heading: float= 0 # [0, 1] 
        self.heading_target: float = 0  # [0, 1]
        self.heading_rate_seconds: float = 2 # From -1 to 0, or 0 to 1
        self.heading_time: float = 0

        self.trajector_planner: TrajectoryPlanner = TrajectoryPlanner()
        self.transition_planner = TransitionPlanner(touchdown_period=0.15, arc_period=0.3, height=0.025)
        self.start_foot_points: Dict[LegName, Point] = {}
        self.end_foot_points: Dict[LegName, Point] = {}

        self.min_loop_rate_seconds: float = 0.050
        self.loop_completion_time_ms: float = 0.0
        self._start()

    ###############################################################################
    # Thread
    ###############################################################################

    def _start(self):
        print(f"[{self.tag}] starting worker thread")
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
                self._check_idle()
                self._process_dt()
                self._process_motion_state_changes()
                self._process_gait_changes()
                self._process_motion_state()

            delta = time() - loop_time

            if delta < self.min_loop_rate_seconds:
                sleep(self.min_loop_rate_seconds - delta)

            with self.lock:
                self.loop_completion_time_ms = (time() - loop_time) * 1000

    def _check_idle(self):
        if self.motion_state is MotionState.WALK:
            if abs(self.motion_parameters.get_forward_raw()) > self.motion_parameters.deadzone:
                self.idle_flag = False
                self.idle_time = time()

            if abs(self.motion_parameters.get_heading_raw()) > self.motion_parameters.deadzone:
                self.idle_flag = False
                self.idle_time = time()

            if time() - self.idle_time > self.idle_time_trigger_seconds:
                if self.idle_flag == False:
                    self.idle_flag = True
                    if self.idle_flag:
                        print(f"[{self.tag}] idle")
                        self.target_motion_state = MotionState.POSE
                        self._create_transition()
        else:
            if self.motion_state is MotionState.TRANSITION:
                self.idle_flag = False
                self.idle_time = time()

    def _process_dt(self):
        self.pose_time += self.pose_time_rate

        if self.motion_parameters.forward_raw > 0:
            dt = scale_value(self.motion_parameters.forward_raw, 0, 1, self.phase_time_rate_slow, self.phase_time_rate_fast)
            self.phase_time += dt
        elif self.motion_parameters.forward_raw < 0:
            dt = scale_value(self.motion_parameters.forward_raw, -1, 0, -self.phase_time_rate_fast, -self.phase_time_rate_slow)
            self.phase_time += dt

        self.transition_time += self.transition_time_rate
       
        #self.heading, self.heading_time = self.motion_parameters.slew_heading(self.heading, self.heading_time, self.heading_rate_seconds)
        self.heading = self.motion_parameters.get_heading_raw()
        # TEMP


    def _process_motion_state_changes(self):
        if self.previous_target_motion_state is not self.target_motion_state:
            self.previous_target_motion_state = self.target_motion_state
            print(f"[{self.tag}] target state changed to: {self.target_motion_state}")

            if self.target_motion_state is MotionState.STAND:
                self.pose_time = 0
                self.motion_state = self.target_motion_state
            else:
                self._create_transition()

    def _process_gait_changes(self):
        if self.motion_state is MotionState.WALK or self.motion_state is MotionState.TRANSITION:
            if self.gait is not self.target_gait:
                self.gait = self.target_gait
                print(f"[{self.tag}] target gait changed to: {self.gait}")
                self._create_transition()

    def _process_motion_state(self):
        if self.motion_state is MotionState.STANDBY:
            pass

        elif self.motion_state is MotionState.STAND:
            ik_parameters = IKParameters()
            ik_parameters.height_translation = scale_value(
                self.pose_time, 0, self.pose_period, IKParameters().height_translation_min, IKParameters().height_translation_neutral
            )

            base_foot_points = self.quad.get_base_foot_points()
            error = self.quad.set_body_pose_by_transform_inputs(ik_parameters, base_foot_points)
            self._set_error(error)

            if self.pose_time > self.pose_period:
                self.motion_state = MotionState.POSE

        elif self.motion_state is MotionState.SIT:
            ik_parameters = IKParameters()
            ik_parameters.height_translation = scale_value(
                self.pose_time, 0, self.pose_period, IKParameters().height_translation_neutral, IKParameters().height_translation_min
            )

            base_foot_points = self.quad.get_base_foot_points()
            error = self.quad.set_body_pose_by_transform_inputs(ik_parameters, base_foot_points)
            self._set_error(error)

            if self.pose_time > self.pose_period:
                self.pose_time = self.pose_period

        elif self.motion_state is MotionState.POSE:
            base_foot_points = self.quad.get_base_foot_points()
            error = self.quad.set_body_pose_by_transform_inputs(self.ik_parameters, base_foot_points)
            self._set_error(error)

        elif self.motion_state is MotionState.WALK:  
            #TEMP
            angular_velocity = self.motion_parameters.get_heading_raw()
            forward_velocity = self.motion_parameters.get_forward_raw()

            base_foot_points = self.quad.get_base_foot_points()
            foot_points = self.trajector_planner.get_foot_points(self.gait, base_foot_points, self.phase_time, angular_velocity, forward_velocity)
            error = self.quad.set_body_pose_by_transform_inputs(IKParameters(), foot_points)
            self._set_error(error)

        elif self.motion_state is MotionState.TRANSITION:
            if self.transition_time < self.transition_planner.get_period():
                foot_points = self.transition_planner.get_foot_positions(self.transition_time, self.start_foot_points, self.end_foot_points)
                error = self.quad.set_body_pose_by_transform_inputs(IKParameters(), foot_points)
                self._set_error(error)
            else:
                self.phase_time = 0
                self.pose_time = 0
                self.motion_state = self.target_motion_state

    def _create_transition(self):
        """Get start and end foot points and init the tranistion"""
        target_foot_points: Dict[LegName, Point] = {}            

        if self.target_motion_state is MotionState.WALK:
            phase_time = 0
            heading = 0
            for leg_name in LegName:
                base_foot_point = self.quad.get_base_foot_point(leg_name)
                foot_point = self.trajector_planner.get_foot_points(self.gait, leg_name, base_foot_point, phase_time, heading)
                target_foot_points[leg_name] = foot_point
        else:
            target_foot_points = self.quad.get_base_foot_points()

        self.motion_state = MotionState.TRANSITION
        self.transition_time = 0
        current_foot_points = self.quad.get_foot_points()
        self.start_foot_points = current_foot_points
        self.end_foot_points = target_foot_points

    def _set_error(self, error: QuadErrorState):
        self.ik_status = Status.ERROR if error is QuadErrorState.KINEMATICS else Status.STANDBY
        self.joint_angle_status = Status.ERROR if error is QuadErrorState.JOINT else Status.STANDBY

    ###############################################################################
    # Methods
    ###############################################################################

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
        allowed_transitions = {
            MotionState.STAND: {MotionState.STANDBY, MotionState.SIT},
            MotionState.SIT: {MotionState.POSE, MotionState.WALK},
            MotionState.POSE: {MotionState.WALK, MotionState.TRANSITION},
            MotionState.WALK: {MotionState.POSE, MotionState.TRANSITION},
        }

        if state in allowed_transitions and self.motion_state in allowed_transitions[state]:
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

    def get_trajectories(self) -> Tuple[Trajectories, Trajectories, Trajectories]:
        with self.lock:
            base_foot_points = self.quad.get_base_foot_points()
            trajectories = None
            rings = None
            transitions = None

            if self.motion_state is MotionState.WALK or self.motion_state is MotionState.TRANSITION:
                (
                    trajectories,
                    rings,
                ) = self.trajector_planner.get_trajectories(self.gait, base_foot_points, self.motion_parameters.get_heading_raw(), self.motion_parameters.forward_raw)
            if self.motion_state is MotionState.TRANSITION:
                transitions = self.transition_planner.get_transitions(self.start_foot_points, self.end_foot_points)
            return trajectories, rings, transitions

    def get_loop_time_ms(self) -> float:
        with self.lock:
            return self.loop_completion_time_ms

    def get_ik_status(self) -> Status:
        with self.lock:
            return self.ik_status

    def get_joint_angle_status(self) -> Status:
        with self.lock:
            return self.joint_angle_status
