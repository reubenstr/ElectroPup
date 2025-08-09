import zmq
from time import sleep, time
from typing import Callable, Optional
from threading import Thread, Event
from dataclasses import dataclass
from typing import Optional
from copy import deepcopy
import json

from input.gamepad_interface import PS4
from quadruped.interfaces import Status
from input.interfaces import TouchCommand, TouchMessage
from quadruped.parameters.ik_parameters import IKParameters
from quadruped.parameters.motion_parameters import MotionParameters

""""
    Get forwarded touch message from the server.py script as provided by the UI
"""

@dataclass
class ControlMessage:
    leftX: float
    leftY: float
    rightX: float
    rightY: float
    command: TouchCommand

class Touch:
    def __init__(self, callback: Optional[Callable[[TouchCommand], None]] = None):
        self.callback = callback

        context = zmq.Context()
        self.socket = context.socket(zmq.PULL)
        self.socket.bind("tcp://127.0.0.1:5560")

        self.ik_parameters = IKParameters()
        self.motion_parameters = MotionParameters()

        self.status: Status = Status.STANDBY

        self.thread_handle = None
        self.exit_event = Event()
        self.last_message_time: float = 0
        self.no_data_timeout_ms: float = 1.0
        self.message_check_rate_ms: float = 0.010

    ###############################################################################
    # Events
    ###############################################################################

    def _send_input_command_as_event(self, event: TouchCommand):
        if self.callback:
            self.callback(event)

    ###############################################################################
    # Mesage
    ###############################################################################

    def process_message(self, message_str: str):

        message: TouchMessage = json.loads(message_str)

        # print('[TOUCH] message received from UI: ', message)

        self.ik_parameters.set_roll(message.leftX)

        self.ik_parameters.set_pitch(message.leftY)
        self.motion_parameters.set_forward_raw(message.leftY)

        self.ik_parameters.set_yaw(message.rightX)
        self.motion_parameters.set_heading_x(message.rightX)    

        self.ik_parameters.set_height_translation(message.rightY)
        self.motion_parameters.set_heading_y(message.rightY)
           
        if message.command != TouchCommand.NO_UPDATE:   
            self._send_input_command_as_event(message.command)
        

    ###############################################################################
    # Worker (threaded)
    ###############################################################################

    def start(self):
        if not self.thread_handle or not self.thread_handle.is_alive():
            self.thread_handle = Thread(target=self.worker)
            self.thread_handle.start()

    def stop(self):       
        if self.thread_handle and self.thread_handle.is_alive():
            print('[TOUCH] stopping thread')
            self.exit_event.set()
            self.thread_handle.join()

    def worker(self):
        self.exit_event.clear()

        print(f"[TOUCH] thread starting")
        while not self.exit_event.is_set():
            try:
                message = self.socket.recv_string(flags=zmq.NOBLOCK)
                self.last_message_time = time()
                self.status = Status.ACTIVE
                self.process_message(message)
            except zmq.Again:
                if time() - self.last_message_time > self.no_data_timeout_ms:
                    self.status = Status.STANDBY
                sleep(self.message_check_rate_ms)
            except zmq.ZMQError as e:
                print(f"[TOUCH][ZMQ] error: {e}")
                self.status = Status.ERROR
                break
            except Exception as e:
                print(f"[TOUCH][ZMQ] unexpected error: {e}")
                self.status = Status.ERROR
                break

    ###############################################################################
    # Getters / Setters
    ###############################################################################

    def get_ik_parameters(self):
        return deepcopy(self.ik_parameters)

    def get_motion_parameters(self):
        return deepcopy(self.motion_parameters)

    def get_status(self):
        return self.status
