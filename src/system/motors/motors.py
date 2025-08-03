#!/usr/bin/env python
import os
import can
import sys
import traceback
import subprocess
from time import time, sleep
from rich import print  # Overrides print and injects colors
from threading import Thread, Event, Lock
from typing import Dict, List

from motors.motor import Motor
from motors.motor_list import motor_list
from motors.interfaces import CanInfo, MotorZeroInfo
from interfaces import Status

"""
    Controls a collection of MG4010E-i10v3 actuators on a multiple CAN bus networks.

    See motor.py for motor information
"""


class Motors:
    def __init__(self, allow_enable: bool):
        self.allow_enable: bool = allow_enable
        self.tag: str = "Motors"

        self.thread_handle = None
        self.exit_event = Event()
        self.data_lock = Lock()

        self.motors_enabled: bool = False
        self.motor_enable_sequence_delay_seconds: float = 0.250
        self.motor_disable_sequence_delay_seconds: float = 0.250     

        self.min_loop_rate_seconds: float = 0.025

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
        self.target_speeds: Dict[str, int] = {}

        default_speed: int = 250

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

        self.worker_startup_timeout_seconds: float = 5.0
        self.start()

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

    def set_zero_to_current_position(self, motor_name: str):
        """Zero requires power cycle to take effect!"""        
        motor = self.motors[motor_name]
        success = motor.cmd_set_zero_to_current_pos()     
        return success

    ###############################################################################
    # All Motors
    ###############################################################################

    def enable_all_motors(self):
        max_attempts = 3
        start = time()
        self.acquire_can_locks()
        for motor in self.motors.values():
            if self.allow_enable and motor.allow_motion:
                print(f"[{self.tag}] enabling motor: {motor.name}")
                attempt = 0
                while True:
                    if motor.cmd_motor_on():
                        break
                    else:
                        attempt += 1
                        print(f"[{self.tag}][ALL] error, failed to enable {motor.name}, attempt number {attempt}!")
                        if attempt > max_attempts:
                            self.motors_enabled = False                         
                            self.release_can_locks()
                            return False
                        sleep(self.motor_enable_sequence_delay_seconds)

                sleep(self.motor_enable_sequence_delay_seconds)
        print(f"[{self.tag}][ALL] enable all motors on completed, time: {time() - start:0.3f}")
        self.motors_enabled = True     
        self.release_can_locks()
        return True

    def disable_all_motors(self):
        start = time()       
        self.acquire_can_locks()
        if self.motors_enabled:
            for motor in self.motors.values():
                if self.allow_enable and motor.allow_motion:
                    print(f"[{self.tag}] disabling motor: {motor.name}")
                    if not motor.cmd_motor_off():
                        print(f"[{self.tag}][ALL] error, disable all motors failed!")
                        return False
                    sleep(self.motor_disable_sequence_delay_seconds)
            print(f"[{self.tag}][ALL] disable all motors off completed, time: {time() - start:0.3f}")
            self.motors_enabled = False
            self.release_can_locks()
            return True

    def clear_errors_all_motors(self):
        start = time()
        self.acquire_can_locks()
        for motor_tag, motor in self.motors.items():
            self.motors[motor_tag].reply_timeout_count = 0            
            if not motor.cmd_clear_motor_errors():
                print(f"[{self.tag}][ALL] error, clear all motor errors failed!")
                return False
        print(f"[{self.tag}][ALL] clear all errors completed, time: {time() - start:0.3f}")
        self.release_can_locks()
        return True

    def set_pid_all_motors(self):
        start = time()
        self.acquire_can_locks()
        for motor_tag, motor in self.motors.items():
            if not motor.cmd_set_pid_to_ram(motor.angle_pid_kp, motor.angle_pid_ki, motor.speed_pid_kp, motor.speed_pid_ki, motor.iq_pid_kp, motor.iq_pid_ki):
                print(f"[{self.tag}][ALL] set all motor PIDs failed!")
                return False
        print(f"[{self.tag}][ALL] set all motor PIDs completed, time: {time() - start:0.3f}")
        self.release_can_locks()
        return True

    """def is_all_motor_angles_within_range(self, tolerance: float):
        with self.lock:
            for motor_name, motor in self.motors.items():
                if self.is_angle_within_range(motor.position_degrees, self.target_positions[motor.name]) == False:
                    # print(motor_name, motor.angle_degrees, motor.target_angle_degrees)
                    return False
            return True
    """

    ###############################################################################
    # Protected Getters, Setters, and Operations
    ###############################################################################

    def set_motor_targets(self, motor_name: str, speed: int, position: float):
        with self.data_lock:
            self.target_speeds[motor_name] = speed
            self.target_positions[motor_name] = position

    def get_motor(self, motor_name: str) -> Motor:
        with self.data_lock:
            return self.motors[motor_name]

    def get_all_motors(self) -> Dict[str, Motor]:
        with self.data_lock:
            return self.motors.copy()

    def get_motor_position(self, motor_name: str) -> float:
        with self.data_lock:
            if motor_name in self.motors:
                return self.motors[motor_name].position_degrees
            return None

    def is_can_error(self) -> bool:
        for can_info in self.can_infos.values():
            if can_info.status == Status.ERROR:
                return True

        if can_info.thread_handle:
            if not can_info.thread_handle.is_alive():
                return True
        return False

    def is_error(self) -> bool:
        if self.is_can_error():
            return True

        with self.data_lock:
            for key, motor in self.motors.items():
                if motor.is_error():
                    return True
        return False

    ###############################################################################
    # Worker (thread)
    ###############################################################################

    def start(self):
        # Get initial positions, start target, and check for offset.
        for key, motor in self.motors.items():
            if motor.allow_comms:
                motor.req_position()
                if motor.position_degrees > 180.0:
                    motor.set_apply_position_offset(True)
                self.target_positions[key] = motor.position_degrees

        self.set_pid_all_motors()

        print(f"[{self.tag}] starting motor worker threads")
        if not all(can_info.status == Status.ACTIVE for can_info in self.can_infos.values()):
            print(f"[{self.tag}] error, unable to start motors, not all CAN interfaces are active!")
            return
        for can_info in self.can_infos.values():
            if not can_info.thread_handle or not can_info.thread_handle.is_alive():
                can_info.thread_handle = Thread(target=self._worker, args=(can_info,))
                can_info.thread_handle.start()

    def _stop(self):
        for can_info in self.can_infos.values():
            if can_info.thread_handle and can_info.thread_handle.is_alive():
                print(f"[{self.tag}] exiting thread for {can_info.can_channel}")
                can_info.exit_event.set()
                can_info.thread_handle.join(timeout=1)

    def _worker(self, can_info: CanInfo):
        can_info.exit_event.clear()

        print(f"[{self.tag}] worker thread for {can_info.can_channel} started")
        while not can_info.exit_event.is_set():
            loop_time = time()
            for key, motor in self.motors.items():
                if motor.can_channel == can_info.can_channel:
                    target_angle = self.target_positions[key]
                    target_speed = self.target_speeds[key]

                    with can_info.lock:
                        if motor.allow_motion and motor.is_enabled():
                            motor.cmd_set_angle_and_speed(angle=target_angle, speed=target_speed)
                            motor.req_position()
                            #motor.req_state_1()
                            #motor.req_state_2()
                        elif motor.allow_comms:
                            motor.req_position()
                            motor.req_state_1()
                            motor.req_state_2()

                        motor.angle_limit_breached = True if motor.position_degrees < motor.min_angle or motor.position_degrees > motor.max_angle else False

            delta = time() - loop_time

            if delta < self.min_loop_rate_seconds:
                sleep(self.min_loop_rate_seconds - delta)

            can_info.loop_completion_time_ms = (time() - loop_time) * 1000
            # print("LOOP TIME:", can_info.loop_completion_time_ms)
        print(f"[{self.tag}] worker thread for {can_info.can_channel} exited")

    ###############################################################################
    # CAN Helpers
    ###############################################################################

    def acquire_can_locks(self):
        for can_name, can_info in self.can_infos.items():           
            can_info.lock.acquire()

    def release_can_locks(self):
        for can_name, can_info in self.can_infos.items():
            can_info.lock.release()

    ###############################################################################
    # General
    ###############################################################################

    def is_motors_enabled(self) -> bool:
        return self.motors_enabled

    def get_can_status(self, can_name: str) -> Status:
        can_info = next((can_info for can_info in self.can_infos.values() if can_info.can_channel == can_name), None)
        if can_info:
            return can_info.status
        else:
            return Status.ERROR

    def get_can_loop_time(self, can_name: str) -> float:
        can_info = next((can_info for can_info in self.can_infos.values() if can_info.can_channel == can_name), None)
        if can_info:
            return can_info.loop_completion_time_ms
        else:
            return 0

    def get_status(self) -> Status:
        if self.is_error():
            return Status.ERROR
        if self.is_motors_enabled():
            return Status.ACTIVE
        else:
            return Status.STANDBY

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

    def get_all_motor_states(self):
        """Pack state for UI"""
        states = {}
        for motor in self.motors.values():
            state = {}
            state["id"] = motor.motor_id
            state["minAngle"] = motor.min_angle
            state["maxAngle"] = motor.max_angle
            state["inverseRotation"] = motor.inverse_rotation
            state["allowComms"] = motor.allow_comms
            state["allowMotion"] = motor.allow_motion
            state["canChannel"] = motor.can_channel
            state["enabled"] = motor.enabled
            state["commsError"] = motor.is_comms_error()

            values = {}
            values["temperature"] = motor.temperature
            values["voltage"] = motor.voltage
            values["watts"] = motor.watts
            values["motorSpeed"] = motor.motor_speed
            values["encoderPosition"] = motor.encoder_position
            values["positionDegrees"] = motor.position_degrees
            state["values"] = values

            faults = {}
            faults["underVoltageProtection"] = motor.under_voltage_protection
            faults["overVoltageProtection"] = motor.over_voltage_protection
            faults["overTemperatureProtection"] = motor.over_temperature_protection
            faults["lostInputProtection"] = motor.lost_input_protection
            state["faults"] = faults
            states[motor.name.name] = state
        return states

    def get_all_motor_zero_info(self) -> List[MotorZeroInfo]:
        """Pack motor info for zeroing script"""
        infos: List[MotorZeroInfo] = []
        for key, motor in self.motors.items():
            infos.append(
                MotorZeroInfo(
                    can_id=motor.can_channel,
                    motor_name=motor.name,
                    motor_id=motor.motor_id,
                    allow_comms=motor.allow_comms,
                    allow_motion=motor.allow_motion,
                    position=motor.position_degrees,
                    comms_error=motor.is_comms_error(),
                    hardware_error=motor.is_hardware_error(),
                )
            )
        return infos

    def shutdown(self):
        self._stop()
        self.disable_all_motors()
        self.deinit_can_buses(self.can_infos)

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
