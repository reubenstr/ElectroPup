from time import time, sleep
from typing import List
from threading import Thread, Lock, Event
from typing import List, Dict
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
    Generates trajectories for walking and rotation.
    Trajectories are a series of foot positions.
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


        self.transitions: Trajectories = None

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
                self._process_target_motion_state()   
                self._process_motion_state()
                self.temp()

            delta = time() - loop_time

            if delta < self.min_loop_rate_seconds:
                sleep(self.min_loop_rate_seconds - delta)

            with self.lock:
                self.loop_completion_time_ms = (time() - loop_time) * 1000

    def _set_error(self, error: QuadErrorState):
        self.ik_status = Status.ERROR if error is QuadErrorState.KINEMATICS else Status.STANDBY
        self.joint_angle_status = Status.ERROR if error is QuadErrorState.JOINT else Status.STANDBY


    def _process_target_motion_state(self):     
        if self.previous_target_motion_state is not self.target_motion_state:
            self.motion_state = MotionState.TRANSITION
            print(f"[{self.tag}] target state changed to: {self.target_motion_state}")

            target_foot_points: Dict[LegName, Point] = {}

            if self.target_motion_state is MotionState.STANDBY:
                pass

            elif self.target_motion_state is MotionState.STAND:
                pass

            elif self.target_motion_state is MotionState.SIT:
                pass

            elif self.target_motion_state is MotionState.POSE:
                target_foot_points = self.quad.get_base_foot_points()

            elif self.target_motion_state is MotionState.WALK:                
                self.gait_time = 0
                heading = 0                
                for leg_name in LegName:                   
                    base_foot_point = self.quad.get_base_foot_point(leg_name)
                    foot_point = self.trajector_planner.get_foot_point(self.gait, leg_name, base_foot_point, self.gait_time, heading)
                    target_foot_points[leg_name] = foot_point

            
            
          
           
    def temp(self):
        active_foot_points = self.quad.get_foot_points()
        #target_foot_points: Dict[LegName, Point] = {}
        target_foot_points = self.quad.get_base_foot_points()

        ##print(active_foot_points[LegName.FL])

        #self.gait_time = 0
        #heading = 0                
        #for leg_name in LegName:                   
        #    base_foot_point = self.quad.get_base_foot_point(leg_name)
        #    foot_point = self.trajector_planner.get_foot_point(self.gait, leg_name, base_foot_point, self.gait_time, heading)
        #    target_foot_points[leg_name] = foot_point

        ###################################################
        # lower all feet
        # arc one at a time
        # profit

        tp = TransitionPlanner( 
        period=1.0,
        duty_factor=0.25,
        phase_offsets={
            LegName.FL: 0.0,
            LegName.BR: 0.25,
            LegName.FR: 0.5,
            LegName.BL: 0.75,
        })

        timestep = tp.period / 100
        gait_times = np.arange(0, tp.period, timestep)     

        self.transitions: Trajectories = []
        for leg_name in LegName:
            active_foot_point = active_foot_points[leg_name]
            target_foot_point = target_foot_points[leg_name]
         
            transition: Trajectory = []
            for gait_time in gait_times:

                phase, phase_time = tp.get_leg_phase_time(leg_name, gait_time)  
                foot_point = tp.foot_trajectory_sin(phase, phase_time, active_foot_point, target_foot_point)
               

                #foot_point.move_xyz(base_foot_point.x, base_foot_point.y, base_foot_point.z)

                #foot_point, bend_radius, cor = tp._calculate_foot_point(gait, leg_name, base_foot_point, gait_time, heading)
                transition.append(foot_point)            
            self.transitions.append(transition)
            break
                         


    def _process_motion_state(self):
        if self.motion_state is MotionState.STANDBY:
            pass

        elif self.motion_state is MotionState.STAND:
            pass

        elif self.motion_state is MotionState.SIT:
            pass

        elif self.motion_state is MotionState.POSE:
            base_foot_points = self.quad.get_base_foot_points()
            error = self.quad.set_body_pose_by_transform_inputs(self.ik_parameters, base_foot_points)
            self._set_error(error)

        elif self.motion_state is MotionState.WALK:
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

        elif self.motion_state is MotionState.TRANSITION:


            self.motion_state = self.target_motion_state
            print(f"[{self.tag}] motion state changed to: {self.motion_state}")
        

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
   
    def get_trajectories(self) -> Trajectories:
        with self.lock:
            base_foot_points = self.quad.get_base_foot_points()

            a, b, c = self.trajector_planner.get_trajectories(self.gait, base_foot_points, self.motion_parameters.heading_raw)
            self.transitions
            return a, b, self.transitions

    def get_loop_time_ms(self) -> float:
        with self.lock:
            return self.loop_completion_time_ms

    def get_ik_status(self) -> Status:
        with self.lock:
            return self.ik_status

    def get_joint_angle_status(self) -> Status:
        with self.lock:
            return self.joint_angle_status
