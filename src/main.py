#!/usr/bin/env python3

import os
import time
import argparse
import traceback
import subprocess
from math import pi
from time import sleep
from rich import print  # Overrides print and injects colors
from math import degrees
from typing import List, Dict

from system.quadruped.quad import Quad
from system.quadruped.gait_planner import Gait
from system.quadruped.interfaces import LegName, AngleUnits, QuadErrorState
from system.input.input import Input
from system.quadruped.motion import Motion
from system.hardware.hardware import Hardware
from system.motors.motors import Motor, Motors
from system.motors.interfaces import MotorName
from system.auxiliary.aux import Aux, AuxMessage
from system.utilities.utilities import *

from system.interfaces import SystemStates, OpModes, MotorSpeeds, MotorCurrents, Status, InputCommand, MotionState
from system.status import SystemStatus
from system.forwarder import Forwarder

"""
    ElectroPup main application.
"""


class Main:
    def __init__(self, mode: OpModes):
        self.op_mode: OpModes = mode

        print(f"[MAIN] starting in operation mode: {self.op_mode}")

        allow_enable = True if self.op_mode == OpModes.LIVE else False

        self.hardware = Hardware()
        self.input = Input(callback=self.controller_event_callback)
        self.motion = Motion()
        self.forwarder = Forwarder()
        self.motors = Motors(allow_enable)
        # self.aux = Aux()

        self.main_loop_rate_ms = 0.025
        self.loop_time: float = 0
        self.loop_completion_time_ms: float = 0    

    ###############################################################################
    # Callback from Input(s)
    ###############################################################################

    def controller_event_callback(self, event: InputCommand):
        print(f"[MAIN] Controller event received: {event.name}")

        if event == InputCommand.STAND:
            self.motion.set_target_motion_state(MotionState.STAND)

        if event == InputCommand.SIT:
            self.motion.set_target_motion_state(MotionState.SIT)

        if event == InputCommand.POSE:
            self.motion.set_target_motion_state(MotionState.POSE)

        if event == InputCommand.WALK:
            self.motion.set_target_motion_state(MotionState.WALK)

        if event == InputCommand.GAIT_WALK:
            self.motion.set_target_gait(Gait.WALK)

        if event == InputCommand.GAIT_TROT:
            self.motion.set_target_gait(Gait.TROT)

        if event == InputCommand.CLEAR_ERRORS:
            self.clear_errors()

    ###############################################################################
    # Main Loop
    ###############################################################################

    def run(self):
        while True:

            self.update_inputs()

            self.apply_joints_angles()

            # self.process_aux()

            self.forward_states()

            self.sleep_loop()

    ###############################################################################
    # Loop Methods
    ###############################################################################
 
    def update_inputs(self):
        self.motion.set_ik_parameters(self.input.get_ik_parameters())
        self.motion.set_motion_parameters(self.input.get_motion_parameters())

    def apply_joints_angles(self):
         if not self.motors.is_error():
            if self.motion.motion_state is not MotionState.STANDBY:

                if self.motion.motion_state is MotionState.SIT or self.motion.motion_state is MotionState.STAND:
                    speed = 1000
                else:
                    speed = 2000

                joint_angles = self.motion.get_quad().get_joint_angles(AngleUnits.DEGREES)
                self.motors.set_motor_targets(MotorName.FLA, speed, joint_angles[LegName.FL]["abduction"])
                self.motors.set_motor_targets(MotorName.FLH, speed, joint_angles[LegName.FL]["hip"])
                self.motors.set_motor_targets(MotorName.FLK, speed, joint_angles[LegName.FL]["knee"])
                self.motors.set_motor_targets(MotorName.FRA, speed, joint_angles[LegName.FR]["abduction"])
                self.motors.set_motor_targets(MotorName.FRH, speed, joint_angles[LegName.FR]["hip"])
                self.motors.set_motor_targets(MotorName.FRK, speed, joint_angles[LegName.FR]["knee"])
                self.motors.set_motor_targets(MotorName.BLA, speed, joint_angles[LegName.BL]["abduction"])
                self.motors.set_motor_targets(MotorName.BLH, speed, joint_angles[LegName.BL]["hip"])
                self.motors.set_motor_targets(MotorName.BLK, speed, joint_angles[LegName.BL]["knee"])
                self.motors.set_motor_targets(MotorName.BRA, speed, joint_angles[LegName.BR]["abduction"])
                self.motors.set_motor_targets(MotorName.BRH, speed, joint_angles[LegName.BR]["hip"])
                self.motors.set_motor_targets(MotorName.BRK, speed, joint_angles[LegName.BR]["knee"])

    def process_aux(self):
        """
        Check for commands and send latest status data to Auxiliary Board.
        """

        message = AuxMessage()
        message.joint_angle_error = self.body_error_state == Quad.QuadErrorState.JOINT
        message.inverse_kinematics_error = self.body_error_state == Quad.QuadErrorState.KINEMATICS
        message.joystick_error = self.input.gamepad.is_connected() == False
        message.can_error = self.motor_interface_front.is_can_error() or self.motor_interface_back.is_can_error()
        message.imuError = False

        voltage_accumulator: float = 0.0
        motors: Dict[str, Motor] = self.motor_interface_front.get_all_motors() | self.motor_interface_back.get_all_motors()
        for index, (motor_tag, motor) in enumerate(motors.items()):
            message.motor_ons[index] = motor.is_enabled()
            message.motor_errors[index] = motor.is_error()
            if motor.angle_limit_breached == True:
                message.physical_limit_error = True
            if motor.over_temperature_protection == True:
                message.over_temperature_error = True
            if motor.under_voltage_protection == True:
                message.under_voltage_error = True
            if motor.is_comms_error() == True:
                message.motor_communication_error = True
            voltage_accumulator += motor.voltage

        message.battery_voltage = voltage_accumulator / len(motors)

        if time.time() - self.gamepad_last_battery_check_time > self.gamepad_battery_check_rate_seconds:
            self.gamepad_last_battery_check_time = time.time()
            self.gamepad_battery_percent = self.gamepad.get_battery_percentange() or -1

        message.gamepad_battery_percent = self.gamepad_battery_percent

        self.aux.send_at_rate(message.pack(), self.aux_send_rate_seconds)

    def forward_states(self):
        system_status = SystemStatus()
        system_status.opMode.state = self.op_mode

        system_status.motion.state = self.motion.get_motion_state()
        system_status.target_motion.state = self.motion.get_target_motion_state()
        system_status.gait.state = self.motion.get_gait()
        system_status.ik.status = self.motion.get_ik_status()
        system_status.joint_angle.status = self.motion.get_joint_angle_status()
        system_status.input.state = self.input.get_input_mode()
        system_status.loopTimes.main = self.loop_completion_time_ms
        system_status.loopTimes.motion = self.motion.get_loop_time_ms()
        system_status.loopTimes.can0 = self.motors.get_can_loop_time("can0")
        system_status.loopTimes.can1 = self.motors.get_can_loop_time("can1")

        # system_status.gpio.status = self.hardware.get_gpio_status()
        system_status.smbus.status = self.hardware.get_smbus_status()
        # system_status.power_sensor.status = self.hardware.get_power_sensor_status()
        system_status.imu.status = self.hardware.get_imu_status()
        system_status.imu.roll = self.hardware.get_imu_data().roll
        system_status.imu.pitch = self.hardware.get_imu_data().pitch
        system_status.can0.status = self.motors.get_can_status("can0")
        system_status.can1.status = self.motors.get_can_status("can1")
        system_status.gamepad.status = self.input.gamepad.get_status()
        system_status.gamepad.battery = self.input.gamepad.get_battery_life_str()

        self.forwarder.set_sim_quad(self.motion.get_quad())
        # self.forwarder.set_live_quad(self.quad_live)
        self.forwarder.set_system_status(system_status)
        # self.forwarder.set_contacts(self.hardware.get_contacts())
        # self.forwarder.set_motors_states(self.motors.get_all_motor_states())

        trajectories, visual_rings, transitions = self.motion.get_trajectories()
        self.forwarder.set_trajectories(trajectories)
        self.forwarder.set_rings(visual_rings)
        self.forwarder.set_transitions(transitions)

        self.forwarder.set_ik_parameters(self.input.get_ik_parameters())

    def sleep_loop(self):
        """
        Keep a consistance loop rate by sleeping the delta of processing time.
        Sleep required to share the CPU.
        """
        delta = time.time() - self.loop_time

        sleep_time = self.main_loop_rate_ms - delta
        if sleep_time > 0:
            sleep(sleep_time)

        # if delta > self.main_loop_rate_ms:
        #    print(f"[MAIN] Warning, loop time exceeded tick rate! Loop time: {delta:0.3f}, tick rate: {self.main_loop_rate_ms:0.3f}")

        # print(f"[Loop] time to complete a loop: {delta:.3f}, sleep time: {sleep_time:.3f}")
        self.loop_completion_time_ms = delta * 1000
        self.loop_time = time.time()

    ###############################################################################
    # Helpers
    ###############################################################################

    def clear_errors(self):
        print("[{MAIN}] clearing errors...")
        # TODO

    def shutdown(self, full_shutdown_flag: bool):
        print("[MAIN] shutdown...")

        # TODO: sit hexapod to avoid hard crashes

        # self.hardware.beep(BeepType.SHUTDOWN)
        # self.motors.shutdown()

        self.hardware.shutdown()
        self.input.shutdown()
        self.motion.shutdown()
        self.forwarder.shutdown()

        if full_shutdown_flag:
            print(f"[MAIN] shutting down system...")
            sleep(1)
            os.system("sudo shutdown now")


###############################################################################
# Entry
###############################################################################
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run in live or simulation mode.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-s", "--sim", action="store_true", help="Run in simulation mode")
    group.add_argument("-l", "--live", action="store_true", help="Run in live mode")
    parser.add_argument("-r", "--reset", action="store_true", help="Restart the service")
    args = parser.parse_args()

    ###############################################################################
    # Process Arguments
    ###############################################################################

    if args.reset:
        try:
            subprocess.run(["sudo", "systemctl", "restart", "live.service"], check=True)
            print("[System] live.service has been restarted.")
        except subprocess.CalledProcessError as e:
            print(f"[System] error, failed to restart live.service: {str(e)}")
        except Exception as e:
            print(str(e))
            print(traceback.format_exc())
        finally:
            exit(1)

    if args.sim:
        mode = OpModes.SIM
    elif args.live:
        mode = OpModes.LIVE

    ###############################################################################
    # Run Main Program
    ###############################################################################

    if is_service_running("live.service"):
        print(f"[Live] error, live.service is running, unable to start live.py")
        exit(1)

    main = Main(mode=mode)

    try:
        main.run()
    except KeyboardInterrupt:
        print("Keyboard interrupt, exiting")
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
    finally:
        main.shutdown(full_shutdown_flag=False)
