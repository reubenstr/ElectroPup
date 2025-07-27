#!/usr/bin/env python
import os
import can
import sys
import traceback
import threading
import subprocess
from dataclasses import dataclass
from time import time, sleep
from rich import print  # Overrides print and injects colors
from threading import Thread, Event, Lock
from typing import Dict
from enum import Enum

# Local
from system.motors.motor import Motor
from system.motors.motor_list import motor_list
from system.interfaces import Status, CanInfo


"""
Controls a collection of MG4010E-i10v3 actuators on a single CAN bus network.

Class expects the hardware ID of the actuators to be [1 to number_of_motors]

Creates a constains stream of target (angle, speed) updates via a thread.

Application should poll for errors and take action such as shutting down the motors.

Actuator driver limitations:
    - The driver does not have a min and max angle, therefore there is a higher risk of collision.
    - CAN is no able to set torque limit, speed limit, etc. Only the UART interface is capable
        of setting these parameters. The torque limit is used to create 'compliance'.

Motor startup angle reading is 0 to 360, but this library uses a -180 to 180 convention.
If motors angles at startup are greater than 180 an offset flag is set and angles readings will be offset by -360.
"""


class Motors:
    def __init__(self, allow_enable: bool):   
        self.allow_enable: bool = allow_enable
        self.tag: str = "Motors"

        self.thread_handle = None
        self.exit_event = Event()
        self.lock = Lock()
        self.comm_lock = Lock()

        self.motor_enable_sequence_delay_seconds: float = 0.250
        self.motor_disable_sequence_delay_seconds: float = 0.125

        self.min_loop_rate_seconds: float = 0.050

        can_channels = list({motor.can_channel for motor in motor_list() if motor.allow_motion or motor.allow_comms})
        self.can_infos: Dict[str, CanInfo] = {}
        for can_channel in can_channels:
            self.can_infos[can_channel] = CanInfo(
                can_channel=can_channel,
                bus=None,
                status=Status.STANDBY,
                thread_handle=None,
                exit_event=Event(),
                lock=Lock(),
            )
        self.init_can_buses(self.can_infos)

        self.motors: Dict[str, Motor] = {}
        self.target_positions: Dict[str, float] = {}
        self.target_speeds: Dict[str, float] = {}
        self.targets_lock = Lock()

        default_speed = 1.0

        for motor in motor_list():
            if motor.can_channel in can_channels:
                self.motors[motor.name] = Motor(
                    name=motor.name,
                    motor_id=motor.id,
                    min_angle=motor.min_angle,
                    max_angle=motor.max_angle,
                    inverse_rotation=motor.inverse_rotation,
                    allow_comms=motor.allow_comms,
                    allow_motion=motor.allow_motion,
                    can_channel=motor.can_channel,
                    bus=self.can_infos[motor.can_channel].bus,
                )
                self.target_positions[motor.name] = 0  # Will be set during enable.
                self.target_speeds[motor.name] = default_speed

    ###############################################################################
    # CAN
    ###############################################################################

    def init_can_buses(self, can_infos: Dict[str, CanInfo]):

        self.deinit_can_buses(can_infos)

        for can_info in can_infos.values():
            print(f"[{self.tag}] upping {can_info.can_channel} interface")

            result = subprocess.run(
                f"sudo ip link set {can_info.can_channel} up type can bitrate 1000000",
                shell=True,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print(f"[{self.tag}] initializing {can_info.can_channel}  bus")
                try:
                    # USB CAN using this firmware:
                    # https://canable.io/getting-started.html#alt-firmware
                    # https://canable.io/updater/canable2.html
                    can_info.bus = can.interface.Bus(interface="socketcan", channel=can_info.can_channel, bitrate=1000000)
                except:
                    print(f"[{self.tag}] error, unable to init {can_info.can_channel}!")
                    can_info.status = Status.ERROR
                    continue

            else:
                print(f"[{self.tag}] error, failed to up {can_info.can_channel}!")
                can_info.status = Status.ERROR
                continue

            can_info.status = Status.ACTIVE

    def deinit_can_buses(self, can_infos: Dict[str, CanInfo]):
        for can_info in can_infos.values():
            # if can_info.status == Status.ACTIVE:
            print(f"[{self.tag}] deinitializing {can_info.can_channel}")
            try:
                if can_info.bus:
                    can_info.bus.shutdown()
                    can_info.status = Status.STANDBY
            except:
                print(f"[{self.tag}] error deinitializing {can_info.can_channel}!")

            print(f"[{self.tag}] downing {can_info.can_channel} interface")
            os.system(f"sudo ifconfig {can_info.can_channel} down")

    ###############################################################################
    # Per Motor
    ###############################################################################

    def set_zero_to_current_position(self, motor_tag: str):
        start = time()
        motor_id = self.motors[motor_tag].id
        success = self.can_interface.cmd_set_zero_to_current_pos(motor_id)
        if success:
            print(f"[{self.tag}][{motor_tag}] command set zero to current position completed, success: {success}, time: {time() - start:0.3f}")
            self.motors[motor_tag].reply_timeout_count = 0
        else:
            self.motors[motor_tag].reply_timeout_count += 1
        return success

    ###############################################################################
    # All Motors
    ###############################################################################

    def enable_all_motors(self):
        start = time()
        with self.comm_lock:
            for motor in self.motors.values():
                if not motor.cmd_motor_on():
                    print(f"[{self.tag}][ALL] error, enable all motors failed!")
                    return False
            print(f"[{self.tag}][ALL] enable all motors on completed, time: {time() - start:0.3f}")
            return True

    def disable_all_motors(self):
        start = time()
        with self.comm_lock:
            self.motors_on = False
            for motor in self.motors.values():
                if not motor.cmd_motor_off():
                    print(f"[{self.tag}][ALL] error, disable all motors failed!")
                    return False
            print(f"[{self.tag}][ALL] disable all motors off completed, time: {time() - start:0.3f}")
            return True

    def clear_errors_all_motors(self):
        start = time()
        with self.comm_lock:
            for motor_tag, motor in self.motors.items():
                self.motors[motor_tag].reply_timeout_count = 0
                if not motor.cmd_clear_motor_errors():
                    print(f"[{self.tag}][ALL] error, clear all motor errors failed!")
                    return False
            print(f"[{self.tag}][ALL] clear all errors completed, time: {time() - start:0.3f}")
            return True

    def set_pid_all_motors(self):
        start = time()
        with self.comm_lock:
            for motor_tag, motor in self.motors.items():
                if not motor.cmd_set_pid_to_ram(
                    motor.angle_pid_kp, motor.angle_pid_ki, motor.speed_pid_kp, motor.speed_pid_ki, motor.iq_pid_kp, motor.iq_pid_ki
                ):
                    print(f"[{self.tag}][ALL] set all motor PIDs failed!")
                    return False
            print(f"[{self.tag}][ALL] set all motor PIDs completed, time: {time() - start:0.3f}")
            return True

    def is_all_motor_angles_within_range(self, tolerance: float):
        with self.lock:
            for motor_name, motor in self.motors.items():
                if self.is_angle_within_range(motor.position_degrees, self.target_positions[motor.name]) == False:
                    # print(motor_name, motor.angle_degrees, motor.target_angle_degrees)
                    return False
            return True

    ###############################################################################
    # Protected Getters, Setters, and Operations
    ###############################################################################

    def set_motor_targets(self, motor_name: str, speed: int, position: float):
        with self.lock:
            self.target_speeds[motor_name] = speed
            self.target_positions[motor_name] = position

    def get_motor(self, motor_name: str):
        with self.lock:
            return self.motors[motor_name]

    def get_all_motors(self):
        with self.lock:
            return self.motors.copy()

    def get_motor_position(self, motor_name: str):
        with self.lock:
            return self.motors[motor_name].position_degrees

    def is_error(self):
        """
        Args: None

        Returns:
            bool: True if motor contains a fault state or comms error
        """
        if self.is_can_error():
            return True

        if self.thread_handle:
            if not self.thread_handle.is_alive():
                return True

        with self.lock:
            error = False
            for motor_tag, motor in self.motors.items():
                if motor.is_error():
                    error = motor_tag
            return error

    ###############################################################################
    # Worker (thread)
    ###############################################################################

    def start(self):
        print(f"[{self.tag}] starting motor worker threads")
        if not all(can_info.status == Status.ACTIVE for can_info in self.can_infos.values()):
            print(f"[{self.tag}] error, unable to start motors, not all CAN interfaces are active!")
            return

        for can_info in self.can_infos.values():
            if not can_info.thread_handle or not can_info.thread_handle.is_alive():
                can_info.thread_handle = threading.Thread(target=self._worker, args=(can_info,))
                can_info.thread_handle.start()

        start = time()
        while True:
            if all(can_info.worker_running_flag for can_info in self.can_infos.values()):
                break
            if time() - start > 5:
                print(f"[{self.tag}] error, work failed to enter running")
                break
            sleep(0.05)

    def _stop(self):
        for can_info in self.can_infos.values():
            if can_info.thread_handle and can_info.thread_handle.is_alive():
                print(f"[{self.tag}] exiting thread for {can_info.can_channel}")
                can_info.exit_event.set()
                can_info.thread_handle.join(timeout=1)

    """
    def _worker_check_all_angle_limits(self)   :
        with self.lock:
            for motor_tag, motor in self.motors.items(): 
                if motor.position_degrees < motor.angle_min or motor.position_degrees > motor.angle_max:
                    self.motors[motor_tag].angle_limit_breached = True 
                    print(f"[{motor_tag}] error, breach! angle: {motor.position_degrees}, min: {motor.angle_min}, max: {motor.angle_max}")
    """

    def _worker(self, can_info: CanInfo):
        can_info.exit_event.clear()

        for key, motor in self.motors.items():
            if motor.allow_comms:
                motor.req_position()
                if motor.position_degrees > 180.0:
                    motor.set_apply_position_offset(True)
                self.target_positions[key] = motor.position_degrees
                # SET MOTOR TARGET?
                # TODO: set PIDs

        can_info.worker_running_flag = True

        while not can_info.exit_event.is_set():
            loop_time = time()
            for key, motor in self.motors.items():
                if motor.can_channel == can_info.can_channel:
                    with self.targets_lock:
                        target_angle = self.target_positions[key]
                        target_speed = self.target_speeds[key]

                    with can_info.lock:
                        if motor.allow_motion and motor.is_enabled():
                            motor.cmd_set_angle_and_speed(angle=target_angle, speed=target_speed)
                            motor.req_position()
                            motor.req_state_1()
                        elif motor.allow_comms:
                            motor.req_position()
                            motor.req_state_1()

                    # check error

            delta = time() - loop_time

            if delta < self.min_loop_rate_seconds:
                sleep(self.min_loop_rate_seconds - delta)

            can_info.loop_completion_time_ms = (time() - loop_time) * 1000
            print("LOOP TIME:", can_info.loop_completion_time_ms)

    ###############################################################################
    # General
    ###############################################################################

    def shutdown(self):
        self._stop()
        self.disable_all_motors()
        self.deinit_can_buses(self.can_infos)

    def is_error(self) -> bool:
        for can_info in self.can_infos.values():
            if can_info.status == Status.ERROR:
                return True

            if can_info.thread_handle:
                if not can_info.thread_handle.is_alive():
                    return True

        for key, motor in self.motors.items():
            if motor.is_error():
                return True
        return False

    ###############################################################################
    # Helpers
    ###############################################################################

    @staticmethod
    def is_angle_within_range(position: float, target: float, tolerance: float) -> bool:
        def normalize(angle):
            """Normalize the angle to be within the range of 0 to 360 degrees."""
            return angle % 360

        difference = abs(normalize(position) - normalize(target))
        return difference <= tolerance or difference >= (360 - tolerance)


###############################################################################
# Main / Entry - For Testing
###############################################################################
if __name__ == "__main__":
    motors = Motors(allow_enable=True)
    motors.start()

    test = 1
    print(f"Starting motor test: {test}")

    try:
        if test == 0:
            while True:
                print(motors.motors["FLA"].position_degrees)
                sleep(0.100)

        elif test == 1:
            motors.enable_all_motors()
            while True:
                motors.set_motor_targets(motor_name="FLA", speed=2000, position=90)
                # motor_set_0.set_motor_targets(motor_tag="FLH", speed=1500, angle=90)
                # motor_set_0.set_motor_targets(motor_tag="FLK", speed=1000, angle=90)
                sleep(2)
                motors.set_motor_targets(motor_name="FLA", speed=2000, position=180)
                # motor_set_0.set_motor_targets(motor_tag="FLH", speed=1500, angle=180)
                # motor_set_0.set_motor_targets(motor_tag="FLK", speed=1000, angle=180)
                sleep(2)

    except Exception as e:
        print(e)
        print(traceback.format_exc())
    except KeyboardInterrupt:
        print("Keyboard interrupt, exiting")
    finally:
        motors.shutdown()
        sys.exit(0)
