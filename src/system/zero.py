#!/usr/bin/env python3
"""
    Utility to zero the MG4010E-i10v3 motors and verify motor layout.
    
    Not all motors are required to be attached.
    
    Motors require a power cycle for a new zero to take effect!
"""

import sys
import time
import math
import threading
from typing import List

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style

from hardware.hardware import Hardware
from motors.motors import Motors
from motors.interfaces import MotorZeroInfo

"""
    This script creates an interface to zero the position of the motors.

"""

motors = Motors(allow_enable=False)

num_motors = 12
motor_infos: List[MotorZeroInfo] = []
selected_index = [0]
exit_event = threading.Event()
zerored_motors = [False] * 12

# Styles for displayed text.
style = Style.from_dict(
    {
        "text": "fg:default bg:default",
        "selected": "fg:blue bg:default bold",
        "error": "fg:red bold",
        "warn": "fg:yellow bold",
        "fault": "fg:yellow bold",
        "ready": "fg:green bold",
    }
)


def clear_screen():
    # ANSI escape codes for "clear screen" and "move cursor to top-left"
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def get_motor_line(i):
    if len(motor_infos) < i + 1:
        return [("class:text", "  No motor data!")]

    info: MotorZeroInfo = motor_infos[i]

    # Pick state label and style
    if info.allow_comms == False:
        state_style = "warn"
        state_text = "COMM DISABLED"
    elif info.comms_error:
        state_style = "error"
        state_text = "COMM ERROR"
    elif info.hardware_error:
        state_style = "fault"
        state_text = "MOTOR FAULT"
    else:
        state_style = "ready"
        state_text = "READY"

    position = f"{info.position:7.2f}"
    motor_name = info.motor_name
    motor_id = info.motor_id
    can_id = info.can_id
    zeroed = "success" if zerored_motors[i] else ""

    line_style = "selected" if i == selected_index[0] else "text"

    return [
        ("class:" + state_style, f"{state_text:13} "),
        (
            "class:" + line_style,
            f"| {position:}° | {motor_id:2} | {motor_name:18} | {can_id} | {zeroed}",
        ),
    ]


motor_windows = [
    Window(
        content=FormattedTextControl(lambda i=i: get_motor_line(i)),
        height=1,
        always_hide_cursor=True,
    )
    for i in range(num_motors)
]

layout = Layout(
    HSplit(
        [
            Window(
                height=1,
                always_hide_cursor=True,
                content=FormattedTextControl(
                    [
                        (
                            "class:text",
                            "   State      |   Angle  | ID |       Name         | CAN  | Zeroed",
                        )
                    ]
                ),
            ),
            Window(
                height=1,
                always_hide_cursor=True,
                content=FormattedTextControl(
                    [
                        (
                            "class:text",
                            "--------------------------------------------------------------------",
                        )
                    ]
                ),
            ),
            *motor_windows,
            Window(
                height=1,
                always_hide_cursor=True,
                content=FormattedTextControl("Use ↑/↓ to move, 0 to zero, q to exit\n"),
                style="reverse",
            ),
            Window(
                height=1,
                always_hide_cursor=True,
                content=FormattedTextControl("Warning: power cycle required for zero to take effect!\n"),
                style="bg:darkred",
            ),
        ]
    )
)

kb = KeyBindings()

@kb.add("up")
def move_up(event):
    selected_index[0] = (selected_index[0] - 1) % num_motors


@kb.add("down")
def move_down(event):
    selected_index[0] = (selected_index[0] + 1) % num_motors


@kb.add("0")
def select(event):
    motor_name = motor_infos[selected_index[0]].motor_name
    success = motors.set_zero_to_current_position(motor_name)
    if success:
        zerored_motors[selected_index[0]] = True



@kb.add("c-c")
@kb.add("q")
def _(event):
    clear_screen()
    print("Shutting down...")
    exit_event.set()
    motors.shutdown()   
    event.app.exit()


app = Application(layout=layout, key_bindings=kb, style=style, full_screen=True)


def update_periodically():
    global motor_infos
    while not exit_event.is_set():
        motor_infos = motors.get_all_motor_zero_info()
        app.invalidate()
        time.sleep(0.05)


threading.Thread(target=update_periodically, daemon=True).start()


###############################################################################
# Entry
###############################################################################
if __name__ == "__main__":
    clear_screen()
    app.run()
