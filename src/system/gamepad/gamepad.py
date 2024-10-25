#!/usr/bin/env python3

"""
    Converts gamepad inputs into motion parameters ready to be consumed by kinematics calculations.

    Assumes a PS4 controller is used by default; other controllers are possible with code changes.
"""

import copy
from time import sleep
from typing import Callable, Optional

from .gamepad_interface import PS4
from ..parameters.motion_parameters import (
    MotionParameters,
    KineticState,
    ControllerEvent,
)


class Gamepad:
    def __init__(self, motion_parameters: MotionParameters):
        self.motion_parameters = motion_parameters

        self.controller_event_callback: Optional[Callable[[ControllerEvent], None]] = (
            None
        )

        self.kinetic_state: KineticState = KineticState.INIT

        # Find the ID of the connected joystick (gamepad): "ls /dev/input/ | grep js"
        joystick_number = 0
        self.gamepad = PS4(joystick_number)

        # if self.gamepad.isConnected():
        self.gamepad.addButtonChangedHandler("TRIANGLE", self.btn_triangle_changed_callback)
        self.gamepad.addButtonChangedHandler("CIRCLE", self.btn_circle_changed_callback)
        self.gamepad.addButtonChangedHandler("CROSS", self.btn_cross_changed_callback)
        self.gamepad.addButtonChangedHandler("SQUARE", self.btn_square_changed_callback)
        self.gamepad.addButtonChangedHandler("L3", self.btn_l3_changed_callback)
        self.gamepad.addButtonChangedHandler("R3", self.btn_r3_changed_callback)
        self.gamepad.addAxisMovedHandler("LEFT-X", self.axis_left_x_changed_callback)
        self.gamepad.addAxisMovedHandler("LEFT-Y", self.axis_left_y_changed_callback)
        self.gamepad.addAxisMovedHandler("RIGHT-X", self.axis_right_x_changed_callback)
        self.gamepad.addAxisMovedHandler("RIGHT-Y", self.axis_right_y_changed_callback)

    ###############################################################################
    # Events from Interface
    ###############################################################################

    def register_controller_event_callback(
        self, callback: Callable[[ControllerEvent], None]
    ):
        self.controller_event_callback = callback

    def _trigger_controller_event(self, event: ControllerEvent):
        if self.controller_event_callback:
            self.controller_event_callback(event)

    ###############################################################################
    # Callback handlers from Gamepad
    ###############################################################################

    def btn_triangle_changed_callback(self, state):
        if state:
            self._trigger_controller_event(ControllerEvent.KINETIC_STATE_TOGGLE)

    def btn_circle_changed_callback(self, state):
        pass

    def btn_cross_changed_callback(self, state):
        if state:
            self._trigger_controller_event(ControllerEvent.MOTOR_POWER_TOGGLE)

    def btn_square_changed_callback(self, state):
        pass

    def btn_l3_changed_callback(self, state):
        if state and self.gamepad.isPressed("R3"):
            self._trigger_controller_event(ControllerEvent.MOTOR_POWER_TOGGLE)

    def btn_r3_changed_callback(self, state):
        if state and self.gamepad.isPressed("L3"):
            self._trigger_controller_event(ControllerEvent.MOTOR_POWER_TOGGLE)

    def axis_left_x_changed_callback(self, value):
        if self.kinetic_state == KineticState.POSE:
            self.motion_parameters.roll = self._map(
                value,
                -1,
                1,
                self.motion_parameters.roll_min,
                self.motion_parameters.roll_max,
            )
        elif self.kinetic_state == KineticState.MOTION:
            self.motion_parameters.yaw_rate = self._map(
                value,
                -1,
                1,
                self.motion_parameters.yaw_rate_min,
                self.motion_parameters.yaw_rate_max,
            )

    def axis_left_y_changed_callback(self, value):
        if self.kinetic_state == KineticState.POSE:
            self.motion_parameters.pitch = self._map(
                value,
                -1,
                1,
                self.motion_parameters.pitch_min,
                self.motion_parameters.pitch_max,
            )
        elif self.kinetic_state == KineticState.MOTION:
            self.motion_parameters.step_length = self._map(
                value,
                -1,
                1,
                self.motion_parameters.step_length_min,
                self.motion_parameters.step_length_max,
            )

    def axis_right_x_changed_callback(self, value):
        if self.kinetic_state == KineticState.POSE:
            self.motion_parameters.yaw = self._map(
                value,
                -1,
                1,
                self.motion_parameters.yaw_min,
                self.motion_parameters.yaw_max,
            )
        elif self.kinetic_state == KineticState.MOTION:
            self.motion_parameters.yaw_rate = self._map(
                value,
                -1,
                1,
                self.motion_parameters.yaw_rate_min,
                self.motion_parameters.yaw_rate_max,
            )

    def axis_right_y_changed_callback(self, value):
        if self.kinetic_state == KineticState.POSE:
            self.motion_parameters.height_translation = self._map(
                value,
                1,
                -1,
                self.motion_parameters.height_translation_min,
                self.motion_parameters.height_translation_max,
            )
        elif self.kinetic_state == KineticState.MOTION:
            self.motion_parameters.height_translation = self._map(
                value,
                1,
                -1,
                self.motion_parameters.height_translation_min,
                self.motion_parameters.height_translation_max,
            )

    ###############################################################################
    # Methods
    ###############################################################################

    def set_kinetic_state(self, kinetic_state: KineticState):
        self.kinetic_state = kinetic_state

    def get_motion_parameters(self):
        return copy.deepcopy(self.motion_parameters)

    def is_connected(self):
        return self.gamepad.isConnected()

    def disconnect(self):
        self.gamepad.disconnect()

    ###############################################################################
    # Helpers
    ###############################################################################

    def _map(self, n, in_min, in_max, out_min, out_max):
        return (n - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


###############################################################################
# Main - Run to test class.
###############################################################################
if __name__ == "__main__":

    motion_parameters_filepath = "./parameters/motion_parameters.yaml"
    motion_parameters = MotionParameters(motion_parameters_filepath)
    if motion_parameters.is_error():
        print(f"[SYSTEM] parameter file not found! {motion_parameters_filepath}")
        exit(1)

    gamepad_interface = GamepadInterface(motion_parameters)

    try:
        while True:
            motion_parameters = gamepad_interface.get_motion_parameters()
            motion_parameters.print()
            sleep(0.100)

    except KeyboardInterrupt:
        pass

    finally:
        gamepad_interface.disconnect()
