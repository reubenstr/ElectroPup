import re
import zmq
import time
import json
import math
import threading
import numpy as np
from typing import Dict
from math import radians
from copy import deepcopy
from threading import Event
from dataclasses import dataclass, asdict

from system.utilities.key_converter import KeyConverter
from system.status import SystemStatus
from system.quadruped.quad import Quad
from system.interfaces import Contacts
from system.quadruped.parameters.ik_parameters import IKParameters


"""
    Collects system data and fowards the data to API server (server.py)
"""


class Forwarder:
    def __init__(self):
        self.tag = "FORWARDER"

        context = zmq.Context()
        self.socket = context.socket(zmq.PUSH)
        self.socket.bind("tcp://127.0.0.1:5559")

        self.sim_quad = None
        self.live_quad = None
        self.ik_parameters = None
        self.trajectories = None
        self.soft_trajectories = None
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

    def set_soft_trajectories(self, trajectories):
        with self.data_lock:
            self.soft_trajectories = trajectories

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
                data["plotSim"] = self._create_plot_data(self.sim_quad)
                data["plotLive"] = self._create_plot_data(self.live_quad)
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

    def _create_plot_data(self, quad: Quad):
        """
        Convert a hexapod object into points for the UI.
        """

        def scale(value: float) -> float:
            """
            The kinematics uses a different convention that standard ploting libaries,
            therefore rotate the points to match the expected convention of the UI plotting library.
            """
            return round(value * 1000, 2)

        plot = {}
        if quad:

            plot["body"] = {}
            points = quad.get_body_coordinates() + [quad.get_body_coordinates()[0]]
            plot["body"]["name"] = "body"
            plot["body"]["x"] = [scale(point.x) for point in points]
            plot["body"]["y"] = [scale(point.y) for point in points]
            plot["body"]["z"] = [scale(point.z) for point in points]

            plot["legs"] = []
            for key, points in quad.get_leg_coordinates().items():
                leg_data = {}
                leg_data["name"] = key
                leg_data["x"] = [scale(point.x) for point in points]
                leg_data["y"] = [scale(point.y) for point in points]
                leg_data["z"] = [scale(point.z) for point in points]
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
   
        if self.trajectories:
            plot["trajectories"] = []
            for i, points in enumerate(self.trajectories):
                trajectory_data = {}
                trajectory_data["name"] = "leg" + str(i)
                trajectory_data["x"] = [scale(point.x) for point in points]
                trajectory_data["y"] = [scale(point.y) for point in points]
                trajectory_data["z"] = [scale(point.z) for point in points]
                plot["trajectories"].append(trajectory_data)

        if self.soft_trajectories:
            plot["softTrajectories"] = []
            for i, points in enumerate(self.soft_trajectories):
                trajectory_data = {}
                trajectory_data["name"] = "leg" + str(i)
                trajectory_data["x"] = [scale(point.x) for point in points]
                trajectory_data["y"] = [scale(point.y) for point in points]
                trajectory_data["z"] = [scale(point.z) for point in points]
                plot["softTrajectories"].append(trajectory_data)

        if self.rings:
            plot["rings"] = []
            for i, points in enumerate(self.rings):
                ring_set = {}
                ring_set["name"] = "ring" + str(i)
                ring_set["x"] = [scale(point.x) for point in points]
                ring_set["y"] = [scale(point.y) for point in points]
                ring_set["z"] = [scale(point.z) for point in points]
                plot["rings"].append(ring_set)

        return plot
