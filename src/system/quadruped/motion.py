from time import time, sleep
from typing import List
from threading import Thread, Lock, Event
from typing import List, Dict

from system.quadruped.point import Point, add_vectors, get_distance_xy, get_distance_statistics
from system.quadruped.quad import Quad
from system.quadruped.parameters.ik_parameters import IKParameters
from system.quadruped.parameters.motion_parameters import MotionParameters
from system.interfaces import MotionState, Gaits
from system.utilities.utilities import safe_divide, scale_value
from system.quadruped.trajectory_planner import TrajectoryPlanner, Trajectory, Trajectories
from system.interfaces import LegName

"""
    Generates trajectories for walking and rotation.
    Trajectories are a series of foot positions.
"""


class Motion:
    def __init__(self):

        self.tag = 'Motion'



        self.motion_state: MotionState = MotionState.NONE
        self.trajectories: Trajectories = None

        self.ik_parameters = IKParameters()
        self.motion_parameters = MotionParameters()

        self.trajector_planner: TrajectoryPlanner = TrajectoryPlanner()

        self.quad = Quad()

        self.tick_rate_seconds: float = 0.050
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
            with self.lock:
                #foot_points = self.quad.get_base_foot_points()

                foot_points: Dict[LegName, Point] = {}
                for leg_name in LegName:
                    base_foot_point = self.quad.get_base_foot_point(leg_name)
                    foot_point = self.trajector_planner.get_foot_point(leg_name, base_foot_point, time())
                    foot_points[leg_name] = foot_point

                self.quad.set_body_pose_by_transform_inputs(self.ik_parameters, foot_points)


            sleep(self.tick_rate_seconds)

            

 

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

        elif motion_state == MotionState.VECTOR_WALK:
            pass

        elif motion_state == MotionState.BIAS_WALK:
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

    def get_quad(self) -> Quad:
        with self.lock:
            return self.quad


    ### OLD?

    def get_trajectories(self) -> Trajectories:
        return self.trajector_planner.get_trajectories()

    def get_soft_trajectories(self) -> Trajectories:
        return
        if self.soft_transition_flag:
            return self.soft_trajectories
        return []

    def get_motion_state(self) -> MotionState:
        return self.motion_state

    def get_target_motion_state(self) -> MotionState:
        return self.target_motion_state

    def get_visual_rings(self) -> Trajectories:
        return
        if self.motion_state == MotionState.BIAS_WALK:
            return self.trajectory_planner.get_rings()
        else:
            return None

    def set_target_motion_state(self, state: MotionState):
        self.target_motion_state = state

    def is_in_motion(self) -> bool:
        return self.motion_state != MotionState.POSE
  