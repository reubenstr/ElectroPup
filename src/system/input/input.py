from typing import Callable, Optional
from input.gamepad import Gamepad
from input.touch import Touch
from interfaces import InputMode, InputCommand, Status
from quadruped.parameters.motion_parameters import MotionParameters
from quadruped.parameters.ik_parameters import IKParameters

"""
    Multiplexes multiple inputs: gamepad and UI (touch)
"""

class Input:
    def __init__(self, callback: Optional[Callable[[InputCommand], None]] = None):
        self.callback = callback

        self.input_mode = InputMode.GAMEPAD

        self.gamepad = Gamepad(callback=self.gamepad_event_callback)
        self.gamepad.start()

        self.touch = Touch(callback=self.touch_event_callback)
        self.touch.start()

    ###############################################################################
    # Events
    ###############################################################################

    def _check_event_for_input_change(self, event: InputCommand):
        if event == InputCommand.TOUCH_INPUT:
            self.input_mode = InputMode.TOUCH
        elif event == InputCommand.GAMEPAD_INPUT:
            self.input_mode = InputMode.GAMEPAD

    def _send_controller_event(self, event: InputCommand):
        if self.callback:
            self.callback(event)

    def touch_event_callback(self, event: InputCommand):
        self._check_event_for_input_change(event)
        if self.input_mode == InputMode.TOUCH:
            self._send_controller_event(event)

    def gamepad_event_callback(self, event: InputCommand):
        self._check_event_for_input_change(event)
        if self.input_mode == InputMode.GAMEPAD:
            self._send_controller_event(event)

    ###############################################################################
    # Methods
    ###############################################################################

    def shutdown(self):
        self.gamepad.stop()
        self.touch.stop()

    ###############################################################################
    # Getters / Setters
    ###############################################################################

    def get_input_mode(self) -> InputMode:
        return self.input_mode

    def get_motion_parameters(self) -> MotionParameters:
        if self.input_mode == InputMode.GAMEPAD:
            return self.gamepad.get_motion_parameters()
        elif self.input_mode == InputMode.TOUCH:
            return self.touch.get_motion_parameters()

    def get_ik_parameters(self) -> IKParameters:
        if self.input_mode == InputMode.GAMEPAD:
            return self.gamepad.get_ik_parameters()
        elif self.input_mode == InputMode.TOUCH:
            return self.touch.get_ik_parameters()
