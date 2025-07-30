from time import sleep, time
from typing import Callable, Optional
from threading import Thread, Event
from copy import deepcopy
from math import copysign

from system.input.gamepad_interface import PS4
from system.interfaces import Status, InputCommand
from system.quadruped.parameters.ik_parameters import IKParameters
from system.quadruped.parameters.motion_parameters import MotionParameters
from system.utilities.utilities import scale_value

"""
    Converts gamepad inputs into motion parameters ready to be consumed by kinematics calculations.

    Assumes a PS4 controller is used by default; other controllers are possible with code updates.

    Receives inputs from gamepad_inferface via callbacks.
"""

DPAD_DIRECTION_UP = -1
DPAD_DIRECTION_LEFT = -1
DPAD_DIRECTION_CENTER = 0
DPAD_DIRECTION_DOWN = 1
DPAD_DIRECTION_RIGHT = 1

# All axis have a deadzone around the middle where the value is unpredicable
DEADZONE = 0.025


class Gamepad:
    def __init__(self, callback: Optional[Callable[[InputCommand], None]] = None):
        self.callback = callback

        self.ik_parameters = IKParameters()
        self.motion_parameters = MotionParameters()

        # Find the ID of the connected joystick (gamepad): "ls /dev/input/ | grep js"
        joystick_number = 0
        self.gamepad_inferface = PS4(joystick_number)

        # Setup callbacks from the gamepad interface:
        self.gamepad_inferface.addButtonChangedHandler("TRIANGLE", self.btn_triangle_changed_callback)
        self.gamepad_inferface.addButtonChangedHandler("CIRCLE", self.btn_circle_changed_callback)
        self.gamepad_inferface.addButtonChangedHandler("CROSS", self.btn_cross_changed_callback)
        self.gamepad_inferface.addButtonChangedHandler("SQUARE", self.btn_square_changed_callback)
        self.gamepad_inferface.addButtonChangedHandler("L1", self.btn_l1_changed_callback)
        self.gamepad_inferface.addButtonChangedHandler("R1", self.btn_r1_changed_callback)
        self.gamepad_inferface.addButtonChangedHandler("L2", self.btn_l2_changed_callback)
        self.gamepad_inferface.addButtonChangedHandler("R2", self.btn_r2_changed_callback)
        self.gamepad_inferface.addButtonChangedHandler("L3", self.btn_l3_changed_callback)
        self.gamepad_inferface.addButtonChangedHandler("R3", self.btn_r3_changed_callback)
        self.gamepad_inferface.addButtonChangedHandler("SHARE", self.btn_share_changed_callback)
        self.gamepad_inferface.addButtonChangedHandler("OPTIONS", self.btn_options_changed_callback)
        self.gamepad_inferface.addButtonChangedHandler("PS", self.btn_ps_changed_callback)

        self.gamepad_inferface.addAxisMovedHandler("LEFT-X", self.axis_left_x_changed_callback)
        self.gamepad_inferface.addAxisMovedHandler("LEFT-Y", self.axis_left_y_changed_callback)
        self.gamepad_inferface.addAxisMovedHandler("RIGHT-X", self.axis_right_x_changed_callback)
        self.gamepad_inferface.addAxisMovedHandler("RIGHT-Y", self.axis_right_y_changed_callback)
        self.gamepad_inferface.addAxisMovedHandler("DPAD-X", self.axis_dpad_x_changed_callback)
        self.gamepad_inferface.addAxisMovedHandler("DPAD-Y", self.axis_dpad_y_changed_callback)

        self.no_battery_life_text = "N/A"
        self.status = Status.STANDBY
        self.battery_life_percent: float = -1.0
        self.battery_life_str: str = self.no_battery_life_text

        # State containers
        self.left_shift: bool = False
        self.right_shift: bool = False

        # Thread
        self.thread_handle = None
        self.exit_event = Event()
        self.WORKER_SLEEP_TIME_MS: float = 0.025
        self.gamepad_last_battery_check_time: float = 0
        self.gamepad_battery_check_rate_seconds: float = 1.0

    ###############################################################################
    # Events
    ###############################################################################

    def _send_input_command_as_event(self, event: InputCommand):
        if self.callback:
            self.callback(event)

    ###############################################################################
    # Callback handlers from Gamepad
    ###############################################################################

    """ BUTTONS FACE """

    def btn_triangle_changed_callback(self, state):
        if state == True:
            self._send_input_command_as_event(InputCommand.GAIT_WALK)

    def btn_circle_changed_callback(self, state):
        if state == True:
            pass

    def btn_cross_changed_callback(self, state):
        if state == True:
            self._send_input_command_as_event(InputCommand.GAIT_TROT)

    def btn_square_changed_callback(self, state):
        if state == True:
            pass

    """ BUTTONS SHOULDER AND TRIGGER """

    def btn_l1_changed_callback(self, state):
        self.left_shift = state

    def btn_r1_changed_callback(self, state):
        self.right_shift = state

    def btn_l2_changed_callback(self, state):
        if state == True:
            pass

    def btn_r2_changed_callback(self, state):
        if state == True:
            pass

    def btn_l3_changed_callback(self, state):
        if state == True:
            pass

    def btn_r3_changed_callback(self, state):
        if state == True:
            pass

    """ BUTTONS MISC """

    def btn_share_changed_callback(self, state):
        if state == True:
            pass

    def btn_options_changed_callback(self, state):
        if state == True:
            self._send_input_command_as_event(InputCommand.CLEAR_ERRORS)

    def btn_ps_changed_callback(self, state):
        if state == True:
            pass

    """ AXIS D_PAD """

    def axis_dpad_x_changed_callback(self, state):
        if state == DPAD_DIRECTION_LEFT:
            self._send_input_command_as_event(InputCommand.POSE)
        elif state == DPAD_DIRECTION_CENTER:
            pass
        elif state == DPAD_DIRECTION_RIGHT:
            self._send_input_command_as_event(InputCommand.WALK)

    def axis_dpad_y_changed_callback(self, state):
        if state == DPAD_DIRECTION_UP:  
            self._send_input_command_as_event(InputCommand.STAND)
        elif state == DPAD_DIRECTION_CENTER:
            pass
        elif state == DPAD_DIRECTION_DOWN:          
            self._send_input_command_as_event(InputCommand.SIT)

    """ AXIS JOY-STICKS """

    def axis_left_x_changed_callback(self, value):
        self.ik_parameters.roll = scale_value(
            value,
            -1.0,
            1.0,
            self.ik_parameters.roll_min,
            self.ik_parameters.roll_max,
        )

    def axis_left_y_changed_callback(self, value):
        value *= -1

        self.ik_parameters.pitch = scale_value(
            value,
            -1.0,
            1.0,
            self.ik_parameters.pitch_min,
            self.ik_parameters.pitch_max,
        )

        sign = copysign(1, value)
        if abs(value) < DEADZONE:
            self.motion_parameters.update_forward_raw(0)
        else:
            self.motion_parameters.update_forward_raw(
                sign
                * scale_value(
                    abs(value),
                    DEADZONE,
                    1,
                    0,
                    1,
                )
            )

    def axis_right_x_changed_callback(self, value):

        self.ik_parameters.yaw = scale_value(
            value,
            1.0,
            -1.0,
            self.ik_parameters.yaw_min,
            self.ik_parameters.yaw_max,
        )

        sign = copysign(1, value)
        if abs(value) < DEADZONE:
            self.motion_parameters.update_heading_x(0)
        else:
            self.motion_parameters.update_heading_x(
                sign
                * scale_value(
                    abs(value),
                    DEADZONE,
                    1,
                    0,
                    1,
                )
            )

    def axis_right_y_changed_callback(self, value):
        value *= -1

        self.ik_parameters.height_translation = scale_value(
            value,
            -1,
            1,
            self.ik_parameters.height_translation_min,
            self.ik_parameters.height_translation_max,
        )

        sign = copysign(1, value)
        if abs(value) < DEADZONE:
            self.motion_parameters.update_heading_y(0)
        else:
            self.motion_parameters.update_heading_y(
                sign
                * scale_value(
                    abs(value),
                    DEADZONE,
                    1,
                    0,
                    1,
                )
            )

    ###############################################################################
    # Worker (threaded)
    ###############################################################################

    def start(self):
        if not self.thread_handle or not self.thread_handle.is_alive():
            print("[GAMEPAD] starting thread")
            self.thread_handle = Thread(target=self.worker)
            self.thread_handle.start()

    def stop(self):
        if self.thread_handle and self.thread_handle.is_alive():
            print("[GAMEPAD] stopping thread")
            self.exit_event.set()
            self.thread_handle.join()
            self.gamepad_inferface.disconnect()

    def worker(self):
        self.exit_event.clear()
        while not self.exit_event.is_set():
            if self.is_connected():
                if time() - self.gamepad_last_battery_check_time > self.gamepad_battery_check_rate_seconds:
                    self.gamepad_last_battery_check_time = time()

                    percent = self.gamepad_inferface.get_battery_percent()
                    if percent:
                        self.battery_life_percent = percent
                        self.battery_life_str = f"{int(percent)}%"
                        if percent < 20:
                            self.status = Status.WARNING
                        else:
                            self.status = Status.ACTIVE
                    else:
                        self.battery_life_str = "N/A"
                        self.status = Status.ERROR

            else:
                self.status = Status.STANDBY

            sleep(self.WORKER_SLEEP_TIME_MS)

    ###############################################################################
    # Methods
    ###############################################################################

    def disconnect(self):
        self.gamepad_inferface.disconnect()

    ###############################################################################
    # Getters / Setters
    ###############################################################################

    def get_ik_parameters(self) -> IKParameters:
        return deepcopy(self.ik_parameters)

    def get_motion_parameters(self) -> MotionParameters:
        return deepcopy(self.motion_parameters)

    def is_connected(self) -> bool:
        return self.gamepad_inferface.isConnected()

    def get_status(self) -> Status:
        return self.status
    
    def get_battery_life_percent(self) -> float:
        return self.battery_life_percent

    def get_battery_life_str(self) -> str:
        if self.status != Status.ACTIVE:
            return self.no_battery_life_text
        else:
            return self.battery_life_str
