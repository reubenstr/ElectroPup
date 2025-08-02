import zmq
import time
import json
import threading
from copy import deepcopy
from threading import Event
from dataclasses import asdict

from utilities.key_converter import KeyConverter
from status import SystemStatus
from quadruped.quad import Quad
from hardware.interfaces import Contacts
from quadruped.parameters.ik_parameters import IKParameters


"""
    Collects system data and fowards the data to API server (server.py)
"""


class Forwarder:
    def __init__(self):
        self.tag = "Forwarder"

        context = zmq.Context()
        self.socket = context.socket(zmq.PUSH)
        self.socket.bind("tcp://127.0.0.1:5559")

        self.sim_quad = None
        self.live_quad = None
        self.ik_parameters = None
        self.trajectories = None
        self.transitions = None
        self.hold_trajectories = None
        self.rings = None
        self.system_status: SystemStatus = None
        self.contacts: Contacts = None
        self.motor_states = None

        self.message_id: int = 0

        self.message_send_rate_seconds = 0.050
        self.exit_event = Event()
        self.data_lock = threading.Lock()
        self.thread_handle = threading.Thread(target=self._worker)
        self.thread_handle.start()

    ###############################################################################
    # Public Methods
    ###############################################################################

    def set_sim_quad(self, quad: Quad):
        with self.data_lock:
            self.sim_quad = deepcopy(quad)

    def set_live_quad(self, quad: Quad):
        with self.data_lock:
            self.live_quad = deepcopy(quad)

    def set_ik_parameters(self, ik_parameters: IKParameters):
        with self.data_lock:
            self.ik_parameters = ik_parameters

    def set_trajectories(self, trajectories):
        with self.data_lock:
            self.trajectories = trajectories

    def set_transitions(self, trajectories):
        with self.data_lock:
            self.transitions = trajectories

    def set_hold_trajectories(self, trajectories):
        with self.data_lock:
            self.hold_trajectories = trajectories

    def set_rings(self, rings):
        with self.data_lock:
            self.rings = rings

    def set_system_status(self, status: SystemStatus):
        with self.data_lock:
            self.system_status = status

    def set_contacts(self, contacts: Contacts):
        with self.data_lock:
            self.contacts = contacts

    def set_motors_states(self, motor_states):
        with self.data_lock:
            self.motor_states = motor_states

    def shutdown(self):
        print(f"[{self.tag}] stoping thread")
        if self.thread_handle and self.thread_handle.is_alive():
            self.exit_event.set()
            self.thread_handle.join()

    ###############################################################################
    # Worker Methods
    ###############################################################################

    def _worker(self):
        print(f"[{self.tag}] worker thread started")
        while not self.exit_event.is_set():
            data = {}
            self.message_id += 1
            data["timestamp"] = int(time.time() * 1000)
            with self.data_lock:
                data["plotSim"] = self._create_quad_plot_data(self.sim_quad)
                data["plotLive"] = self._create_quad_plot_data(self.live_quad)
                data["plotExtras"] = self._create_extras_plot()
                data["status"] = None if self.system_status is None else asdict(self.system_status)
                data["contacts"] = None if self.contacts is None else asdict(self.contacts)
                data["motors"] = self.motor_states
                data["ikParameters"] = None if self.ik_parameters is None else asdict(self.ik_parameters)

            converted_data = KeyConverter.convert_keys_to_camel_case(data)
            try:
                # print(json.dumps(converted_data))
                self.socket.send_string(json.dumps(converted_data), flags=zmq.NOBLOCK)
            except zmq.Again:
                pass

            time.sleep(self.message_send_rate_seconds)

        print(f"[{self.tag}] worker thread exiting")

    ###############################################################################
    # Private Methods
    ###############################################################################

    def _create_quad_plot_data(self, quad: Quad):
        """Convert a quad object into points for the UI."""

        plot = {}
        if quad:
            plot["body"] = {}
            plot["body"]["name"] = "body"
            plot["body"]["x"] = []
            plot["body"]["y"] = []
            plot["body"]["z"] = []
            for leg_name, point in quad.get_body_coordinates().items():
                plot["body"]["x"].append(self.scale(point.x))
                plot["body"]["y"].append(self.scale(point.y))
                plot["body"]["z"].append(self.scale(point.z))
            plot["body"]["x"].append(plot["body"]["x"][0])
            plot["body"]["y"].append(plot["body"]["y"][0])
            plot["body"]["z"].append(plot["body"]["z"][0])

            plot["legs"] = []
            for leg_name, points in quad.get_leg_coordinates().items():
                leg_data = {}
                leg_data["name"] = leg_name.name
                leg_data["x"] = [self.scale(point.x) for point in points]
                leg_data["y"] = [self.scale(point.y) for point in points]
                leg_data["z"] = [self.scale(point.z) for point in points]
                plot["legs"].append(leg_data)

            """
            plot["mesh"] = {}
            dz = -1
            ground_contacts = quad.ground_contacts()
            plot["mesh"]["name"] = "mesh"
            plot["mesh"]["x"] = [scale(point.x) for point in ground_contacts]
            plot["mesh"]["y"] = [scale(point.y) for point in ground_contacts]
            plot["mesh"]["z"] = [(scale(point.z) + dz) for point in ground_contacts]
            """

        return plot

    def _create_extras_plot(self):
        """Convert trajectories into points for the UI."""
        plot = {}

        if self.trajectories:
            plot["trajectories"] = []
            for i, points in enumerate(self.trajectories):
                trajectory_data = {}
                trajectory_data["name"] = "leg" + str(i)
                trajectory_data["x"] = [self.scale(point.x) for point in points]
                trajectory_data["y"] = [self.scale(point.y) for point in points]
                trajectory_data["z"] = [self.scale(point.z) for point in points]
                plot["trajectories"].append(trajectory_data)

        if self.rings:
            plot["rings"] = []
            for i, points in enumerate(self.rings):
                ring_set = {}
                ring_set["name"] = "ring" + str(i)
                ring_set["x"] = [self.scale(point.x) for point in points]
                ring_set["y"] = [self.scale(point.y) for point in points]
                ring_set["z"] = [self.scale(point.z) for point in points]
                plot["rings"].append(ring_set)

        if self.transitions:
            plot["transitions"] = []
            for i, points in enumerate(self.transitions):
                trajectory_data = {}
                trajectory_data["name"] = "leg" + str(i)
                trajectory_data["x"] = [self.scale(point.x) for point in points]
                trajectory_data["y"] = [self.scale(point.y) for point in points]
                trajectory_data["z"] = [self.scale(point.z) for point in points]
                plot["transitions"].append(trajectory_data)

        if self.hold_trajectories:
            plot["holdTrajectories"] = []
            for i, points in enumerate(self.hold_trajectories):
                trajectory_data = {}
                trajectory_data["name"] = "leg" + str(i)
                trajectory_data["x"] = [self.scale(point.x) for point in points]
                trajectory_data["y"] = [self.scale(point.y) for point in points]
                trajectory_data["z"] = [self.scale(point.z) for point in points]
                plot["holdTrajectories"].append(trajectory_data)

        return plot

    @staticmethod
    def scale(value: float) -> float:
        """
        The kinematics uses a different convention that standard ploting libaries,
        therefore rotate the points to match the expected convention of the UI plotting library.
        """
        return round(value * 1000, 2)
