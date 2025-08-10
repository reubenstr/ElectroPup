from time import time, sleep
from typing import List
from threading import Thread, Lock, Event
from typing import List, Dict, Tuple, Callable
from itertools import product
from rich import print  # Overrides print and injects colors

from quadruped.point import Point, get_distance_xy
from quadruped.quad import Quad, LegName
from quadruped.transition_planner import TransitionPlanner
from quadruped.parameters.ik_parameters import IKParameters
from quadruped.parameters.motion_parameters import MotionParameters
from quadruped.gait_planner import Gait
from quadruped.trajectory_planner import TrajectoryPlanner, Trajectory, Trajectories
from quadruped.interfaces import Status, OpMode, MotionState, LegName, JointName, AngleUnits
from hardware.interfaces import ImuData
from motors.motors import Motors
from motors.interfaces import MotorName, MotorSpeeds
from utilities.utilities import scale_value, angle_difference_deg

"""
    Applies gaits and transitions to the quadruped.
    Processes user inputs such as speed and direction.

    Notes: 

"""


class Motion:
    def __init__(self, op_mode: OpMode):
        self.op_mode = op_mode
        self.tag = "Motion"

        self._get_imu_data: Callable[[], ImuData] = None

        self.trajector_planner: TrajectoryPlanner = TrajectoryPlanner()

        self.motion_state: MotionState = MotionState.STANDBY
        self.target_motion_state: MotionState = MotionState.STANDBY
        self.previous_target_motion_state: MotionState = MotionState.STANDBY
        self.target_gait: Gait = Gait.TROT
        self.trajector_planner.gait = Gait.TROT

        self.quad = Quad()
        self.motion_parameters: MotionParameters = MotionParameters()
        self.ik_parameters: IKParameters = IKParameters()

        self.phase_time: float = 0     
        self.phase_time_rate_fast: float = 0.010

        self.pose_time: float = 0
        self.pose_time_rate: float = 0.005
        self.pose_period: float = 1

        self.transition_time: float = 0
        self.transition_time_rate: float = 0.005

        self.idle_time: float = 0
        self.idle_time_trigger_seconds: float = 500
        self.idle_flag: bool = True

        self.forward_velocity: float = 0
        self.lateral_velocity: float = 0
        self.angular_velocity: float = 0  
        self.angular_velocity_target: float = 0
        self.angular_velocity_slew_rate_seconds: float = 2
        self.angular_velocity_time: float = 0

        self.transition_enable: bool = False
        self.transition_planner = TransitionPlanner(touchdown_period=0.15, arc_period=0.3, height=0.025)
        self.transition_start_foot_points: Dict[LegName, Point] = {}
        self.transition_end_foot_points: Dict[LegName, Point] = {}
        self.transition_angular_velocity: float = 0
        self.transition_lateral_velocity: float = 0
        self.transition_forward_velocity: float = 0
        self.transition_angle_threadhold: float = 20

        self.soft_transition_enable: bool = False
        self.soft_transition_flag: bool = False
        self.soft_transition_legs_started_swing: Dict[LegName, bool] = []
        self.soft_transition_previous_foot_points: Dict[LegName, Point] = self.quad.get_foot_points()

        self.transition_hold_flag: bool = False

        self.lock = Lock()
        self.exit_event = Event()

        if self.op_mode is OpMode.DEV:
            self.set_target_motion_state(MotionState.WALK, force=True)
        elif self.op_mode is OpMode.LIVE:
            self.set_target_motion_state(MotionState.STANDBY)

        allow_enable = True if self.op_mode is OpMode.LIVE else False
        self.motors: Motors = Motors(allow_enable)

        self.loop_min_rate_seconds: float = 0.010
        self.loop_completion_time_ms: float = 0.0
        self._start()

    ###############################################################################
    # Thread
    ###############################################################################

    def _start(self):
        print(f"[{self.tag}] starting worker thread")
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
                self._get_inputs()
                self._process_dt()
                self._process_motion_state_changes()
                self._process_gait_changes()
                self._process_motion_state()
                self._apply_joints_angles()

            delta = time() - loop_time

            if delta < self.loop_min_rate_seconds:
                sleep(self.loop_min_rate_seconds - delta)

            with self.lock:
                self.loop_completion_time_ms = (time() - loop_time) * 1000

    def _check_idle(self):
        if self.motion_state is MotionState.WALK:
            if abs(self.motion_parameters.forward_velocity) > 0:
                self.idle_flag = False
                self.idle_time = time()

            if abs(self.motion_parameters.forward_velocity) > 0:
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

    def _get_inputs(self):
        self.angular_velocity, self.angular_velocity_time = self.motion_parameters.slew_heading(
            self.angular_velocity, self.angular_velocity_time, self.angular_velocity_slew_rate_seconds
        )
        # TEMP SKIP SLEW
        self.forward_velocity = self.motion_parameters.forward_velocity
        self.lateral_velocity = self.motion_parameters.lateral_velocity
        self.angular_velocity = self.motion_parameters.angular_velocity

    def _process_dt(self):
        self.pose_time += self.pose_time_rate

        heading_reate = scale_value(self.motion_parameters.get_left_magnitude(), 0, 1, 0, self.phase_time_rate_fast)
        angular_rate = scale_value(abs(self.motion_parameters.angular_velocity), 0, 1, 0, self.phase_time_rate_fast)
        self.phase_time += max(heading_reate, angular_rate)

        self.transition_time += self.transition_time_rate

    def _process_motion_state_changes(self):
        if self.previous_target_motion_state is not self.target_motion_state:
            self.previous_target_motion_state = self.target_motion_state
            print(f"[{self.tag}] target state changed to: {self.target_motion_state}")

            if self.target_motion_state is MotionState.STANDBY:
                self.motion_state = MotionState.STANDBY
            elif self.target_motion_state is MotionState.STAND:
                self.pose_time = 0
                self.motion_state = MotionState.STAND
            else:
                self._create_transition()

    def _process_gait_changes(self):
        if self.motion_state is MotionState.WALK or self.motion_state is MotionState.TRANSITION:
            if self.trajector_planner.gait is not self.target_gait:
                self.trajector_planner.gait = self.target_gait
                print(f"[{self.tag}] target gait changed to: {self.target_gait}")
                self._create_transition()

    def _process_motion_state(self):
        if self.motion_state is MotionState.STANDBY:
            self._process_motion_state_standby()

        elif self.motion_state is MotionState.STAND:
            self._process_motion_state_stand()

        elif self.motion_state is MotionState.SIT:
            self._process_motion_state_sit()

        elif self.motion_state is MotionState.POSE:
            self._process_motion_state_pose()

        elif self.motion_state is MotionState.WALK:
            self._process_motion_state_walk()

        elif self.motion_state is MotionState.TRANSITION:
            self._process_motion_state_transition()

    ###############################################################################
    # Motion States
    ###############################################################################

    def _process_motion_state_standby(self):
        ik_parameters = IKParameters()
        ik_parameters.height_translation = IKParameters().height_translation_min
        self.quad.set_body_pose_by_transform_inputs(ik_parameters, self.quad.get_base_foot_points())

    def _process_motion_state_stand(self):
        ik_parameters = IKParameters()
        ik_parameters.height_translation = scale_value(
            self.pose_time, 0, self.pose_period, IKParameters().height_translation_min, IKParameters().height_translation_neutral
        )
        self.quad.set_body_pose_by_transform_inputs(ik_parameters, self.quad.get_base_foot_points())

        if self.pose_time > self.pose_period:
            self.motion_state = MotionState.POSE

    def _process_motion_state_sit(self):
        ik_parameters = IKParameters()
        ik_parameters.height_translation = scale_value(
            self.pose_time, 0, self.pose_period, IKParameters().height_translation_neutral, IKParameters().height_translation_min
        )
        self.quad.set_body_pose_by_transform_inputs(ik_parameters, self.quad.get_base_foot_points())

        if self.pose_time > self.pose_period:
            self.pose_time = self.pose_period

    def _process_motion_state_pose(self):
        self.quad.set_body_pose_by_transform_inputs(self.ik_parameters, self.quad.get_base_foot_points())

    def _process_motion_state_walk(self):
        # Get foot points in latest trajectory.
        new_foot_points = self.trajector_planner.get_foot_points(
            self.quad.get_base_foot_points(),
            self.phase_time,
            self.forward_velocity,
            self.lateral_velocity,
            self.angular_velocity,
        )

        if self.transition_hold_flag:
            if self.transition_enable:
                # Large heading changes trigger a transition.
                old_twist_angle = self.trajector_planner.get_twist_angle(
                    self.quad.get_base_foot_points(),
                    LegName.FR,
                    self.phase_time,
                    self.transition_angular_velocity,
                    self.transition_lateral_velocity,
                    self.transition_forward_velocity,
                )
                new_twist_angle = self.trajector_planner.get_twist_angle(
                    self.quad.get_base_foot_points(), LegName.FR, self.phase_time, self.angular_velocity, self.lateral_velocity, self.forward_velocity
                )
                delta = abs(angle_difference_deg(old_twist_angle, new_twist_angle))
                if delta > self.transition_angle_threadhold:
                    print(
                        f"[{self.tag}] abrupt heading change detected, from {round(old_twist_angle, 2)} to {round(new_twist_angle, 2)} with delta {round(delta, 2)}"
                    )
                    self._create_transition()
                    return

            if self.soft_transition_enable and not self.soft_transition_flag:
                # Large distances between current point and target point trigger a soft transition.
                current_foot_points = self.quad.get_foot_points()
                for leg in LegName:
                    distance = get_distance_xy(current_foot_points[leg], new_foot_points[leg])
                    if abs(distance) > 0.050:
                        print(f"[{self.tag}] large walking distance detected, {distance}")
                        self.soft_transition_flag = True
                        self.soft_transition_legs_started_swing = {LegName.FR: False, LegName.FL: False, LegName.BR: False, LegName.BL: False}
                        break

        if self.soft_transition_flag:
            # Update list of legs in or completed the swing phase
            for leg in LegName:
                if self.trajector_planner.is_leg_in_swing(leg, self.phase_time):
                    self.soft_transition_legs_started_swing[leg] = True

            if all(self.soft_transition_legs_started_swing.values()):
                self.soft_transition_flag = False

        if self.soft_transition_flag:
            # Get foot positions from hold.
            old_foot_points = self.trajector_planner.get_foot_points(
                self.quad.get_base_foot_points(),
                self.phase_time,
                self.transition_forward_velocity,
                self.transition_lateral_velocity,
                self.transition_angular_velocity,
            )

            # Select which trajectory to apply to foot
            combined_foot_points: Dict[LegName, Point] = {}
            for leg in LegName:
                combined_foot_points[leg] = new_foot_points[leg] if self.soft_transition_legs_started_swing[leg] else old_foot_points[leg]    

            self.quad.set_body_pose_by_transform_inputs(IKParameters(), combined_foot_points)
        else:
            self.transition_angular_velocity = self.angular_velocity
            self.transition_lateral_velocity = self.lateral_velocity
            self.transition_forward_velocity = self.forward_velocity
            self.quad.set_body_pose_by_transform_inputs(IKParameters(), new_foot_points)

        self.transition_hold_flag = True

    def _process_motion_state_transition(self):
        if self.transition_time < self.transition_planner.get_period():
            combined_foot_points = self.transition_planner.get_foot_positions(
                self.transition_time, self.transition_start_foot_points, self.transition_end_foot_points
            )
            self.quad.set_body_pose_by_transform_inputs(IKParameters(), combined_foot_points)
        else:
            self.phase_time = 0
            self.pose_time = 0
            self.motion_state = self.target_motion_state
            self.transition_hold_flag = False
            self.soft_transition_flag = False

    ###############################################################################
    # Motion State Helpers
    ###############################################################################

    def _create_transition(self):
        """Get start and end foot points and init the tranistion"""
        target_foot_points: Dict[LegName, Point] = {}

        if self.target_motion_state is MotionState.WALK:
            phase_time = 0
            target_foot_points = self.trajector_planner.get_foot_points(
                self.quad.get_base_foot_points(),
                phase_time,
                self.forward_velocity,
                self.lateral_velocity,
                self.angular_velocity,
            )
        else:
            target_foot_points = self.quad.get_base_foot_points()

        self.motion_state = MotionState.TRANSITION
        self.transition_time = 0
        self.transition_start_foot_points = self.quad.get_foot_points()
        self.transition_end_foot_points = target_foot_points
        self.transition_angular_velocity = self.angular_velocity
        self.transition_forward_velocity = self.forward_velocity

    ###############################################################################
    # Motors
    ###############################################################################

    def _apply_joints_angles(self):
        if self.motors.is_error() or self.quad.get_ik_error() or self.quad.get_joint_angle_error():
            return

        if self.motion_state is MotionState.STANDBY or self.motion_state is MotionState.SIT or self.motion_state is MotionState.STAND:
            speed = MotorSpeeds.SLOW
        else:
            speed = MotorSpeeds.MOTION

        joint_angles = self.quad.get_joint_angles(AngleUnits.DEGREES)
        self.motors.set_motor_targets(MotorName.FLA, speed, joint_angles[LegName.FL][JointName.ABDUCTION])
        self.motors.set_motor_targets(MotorName.FLH, speed, joint_angles[LegName.FL][JointName.HIP])
        self.motors.set_motor_targets(MotorName.FLK, speed, joint_angles[LegName.FL][JointName.KNEE])
        self.motors.set_motor_targets(MotorName.FRA, speed, joint_angles[LegName.FR][JointName.ABDUCTION])
        self.motors.set_motor_targets(MotorName.FRH, speed, joint_angles[LegName.FR][JointName.HIP])
        self.motors.set_motor_targets(MotorName.FRK, speed, joint_angles[LegName.FR][JointName.KNEE])
        self.motors.set_motor_targets(MotorName.BLA, speed, joint_angles[LegName.BL][JointName.ABDUCTION])
        self.motors.set_motor_targets(MotorName.BLH, speed, joint_angles[LegName.BL][JointName.HIP])
        self.motors.set_motor_targets(MotorName.BLK, speed, joint_angles[LegName.BL][JointName.KNEE])
        self.motors.set_motor_targets(MotorName.BRA, speed, joint_angles[LegName.BR][JointName.ABDUCTION])
        self.motors.set_motor_targets(MotorName.BRH, speed, joint_angles[LegName.BR][JointName.HIP])
        self.motors.set_motor_targets(MotorName.BRK, speed, joint_angles[LegName.BR][JointName.KNEE])

    ###############################################################################
    # Methods
    ###############################################################################

    def shutdown(self):
        self.motors.shutdown()
        self._stop()

    def set_get_imu_data_callback(self, func: Callable[[], ImuData]) -> None:
        self._get_imu_data = func

    def get_imu_data(self):
        if self._get_imu_data is None:
            raise RuntimeError("IMU data callback not set")     
        return self._get_imu_data()     

    ###############################################################################
    # Getters / Setters
    ###############################################################################

    def set_ik_parameters(self, ik_parameters: IKParameters):
        with self.lock:
            self.ik_parameters = ik_parameters

    def set_motion_parameters(self, motion_parameters: MotionParameters):
        with self.lock:
            self.motion_parameters = motion_parameters

    def set_target_motion_state(self, state: MotionState, force: bool = False):
        if force:
            self.target_motion_state = state
            return

        if state is MotionState.STANDBY:
            with self.lock:
                self.target_motion_state = state
            return

        allowed_transitions = {
            # target state : {current states}
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

    @property
    def gait(self) -> Gait:
        with self.lock:
            return self.trajector_planner.gait

    def get_target_gait(self) -> Gait:
        with self.lock:
            return self.target_gait

    def get_quad(self) -> Quad:
        with self.lock:
            return self.quad

    def get_trajectories(self) -> Tuple[Trajectories, Trajectories, Trajectories, Trajectories]:

        trajectories = None
        rings = None
        transitions = None
        hold_trajectories = None

        if self.motion_state is MotionState.WALK or self.motion_state is MotionState.TRANSITION:
            (
                trajectories,
                rings,
            ) = self.trajector_planner.get_trajectories(self.quad.get_base_foot_points(), self.forward_velocity, self.lateral_velocity, self.angular_velocity)

            if self.soft_transition_flag or self.motion_state is MotionState.TRANSITION:
                (
                    hold_trajectories,
                    old_rings,
                ) = self.trajector_planner.get_trajectories(
                    self.quad.get_base_foot_points(), self.transition_forward_velocity, self.transition_lateral_velocity, self.transition_angular_velocity
                )

        if self.motion_state is MotionState.TRANSITION:
            transitions = self.transition_planner.get_transitions(self.transition_start_foot_points, self.transition_end_foot_points)

        return trajectories, rings, transitions, hold_trajectories

    def get_loop_time_ms(self) -> float:
        with self.lock:
            return self.loop_completion_time_ms
