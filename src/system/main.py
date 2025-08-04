#!/usr/bin/env python3

import os
import argparse
import traceback
import subprocess
from time import sleep, time
from rich import print  # Overrides print and injects colors
from typing import Dict, List

from quadruped.quad import Quad
from quadruped.gait_planner import Gait
from quadruped.interfaces import LegName, JointName, AngleUnits, MotionState
from input.interfaces import TouchCommand
from input.input import Input
from quadruped.motion import Motion
from hardware.hardware import Hardware
from motors.motors import Motor, Motors
from motors.interfaces import MotorName, MotorSpeeds
from auxiliary.aux import Aux, AuxMessage
from utilities.utilities import *
from interfaces import OpModes, Status
from status import SystemStatus
from forwarder import Forwarder

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
        self.aux = Aux()

        self.main_loop_rate_seconds = 0.025
        self.main_loop_time: float = 0
        self.main_loop_completion_time_ms: float = 0

        if self.op_mode == OpModes.SIM:
            self.motion.set_target_motion_state(MotionState.WALK, force=True)
        elif self.op_mode == OpModes.LIVE:
            self.motion.set_target_motion_state(MotionState.STANDBY)

    ###############################################################################
    # Callback from Input(s)
    ###############################################################################

    def controller_event_callback(self, event: TouchCommand):

        if event is TouchCommand.DISABLE_ENABLE_MOTORS:
            if self.op_mode is OpModes.LIVE:
                if self.motors.is_motors_enabled():
                    self.motors.disable_all_motors()
                    self.motion.set_target_motion_state(MotionState.STANDBY)
                else:
                    self.motors.enable_all_motors()
            else:
                print(f"[MAIN] Warning, enable/disable motors blocked, LIVE operation mode not enabled.")

        if event is TouchCommand.CLEAR_ERRORS:
            self.clear_errors()
            return
        
        if self.op_mode is OpModes.LIVE:
            if self.motion.get_motion_state() is MotionState.STANDBY:
                if not self.motors.is_motors_enabled():
                    print(f"[MAIN] Controller event {event.name} blocked, motors not enabled.")
                    return

        if event is TouchCommand.STAND:
            self.motion.set_target_motion_state(MotionState.STAND)
            self.motor_enable_flag = True

        if event is TouchCommand.SIT:
            self.motion.set_target_motion_state(MotionState.SIT)

        if event is TouchCommand.POSE:
            self.motion.set_target_motion_state(MotionState.POSE)

        if event is TouchCommand.WALK:
            self.motion.set_target_motion_state(MotionState.WALK)

        if event is TouchCommand.GAIT_WALK:
            self.motion.set_target_gait(Gait.WALK)

        if event is TouchCommand.GAIT_TROT:
            self.motion.set_target_gait(Gait.TROT)

        print(f"[MAIN] Controller event received: {event.name}")

    ###############################################################################
    # Main Loop
    ###############################################################################

    def run(self):
        while True:

            self.update_inputs()

            self.apply_joints_angles()

            self.process_aux()

            self.forward_states()

            self.sleep_loop()

    ###############################################################################
    # Loop Methods
    ###############################################################################

    def update_inputs(self):
        self.motion.set_ik_parameters(self.input.get_ik_parameters())
        self.motion.set_motion_parameters(self.input.get_motion_parameters())

    def apply_joints_angles(self):
        if self.motors.is_error() or \
            self.motion.get_quad().get_ik_error() or \
            self.motion.get_quad().get_joint_angle_error():
            return

        if self.motion.motion_state is MotionState.STANDBY or \
            self.motion.motion_state is MotionState.SIT or \
            self.motion.motion_state is MotionState.STAND:
            speed = MotorSpeeds.SLOW
        else:
            speed = MotorSpeeds.MOTION
  
        joint_angles = self.motion.get_quad().get_joint_angles(AngleUnits.DEGREES)
        self.motors.set_motor_targets(MotorName.FLA, speed, joint_angles[LegName.FL][JointName.ABDUCTION])
        self.motors.set_motor_targets(MotorName.FLH, speed, joint_angles[LegName.FL][JointName.HIP])
        self.motors.set_motor_targets(MotorName.FLK, speed, joint_angles[LegName.FL][JointName.KNEE])
        self.motors.set_motor_targets(MotorName.FRA, speed, joint_angles[LegName.FR][JointName.ABDUCTION])
        self.motors.set_motor_targets(MotorName.FRH, speed, joint_angles[LegName.FR][JointName.HIP])
        self.motors.set_motor_targets(MotorName.FRK, speed, joint_angles[LegName.FR][JointName.KNEE])
        self.motors.set_motor_targets(MotorName.BLA, speed, joint_angles[LegName.BL][JointName.ABDUCTION])
        self.motors.set_motor_targets(MotorName.BLH, speed, joint_angles[LegName.BL][JointName.HIP])
        self.motors.set_motor_targets(MotorName.BLK, speed, joint_angles[LegName.BL][JointName.KNEE])
        self.motors.set_motor_targets(MotorName.BRA, speed, joint_angles[LegName.BR][JointName.ABDUCTION])
        self.motors.set_motor_targets(MotorName.BRH, speed, joint_angles[LegName.BR][JointName.HIP])
        self.motors.set_motor_targets(MotorName.BRK, speed, joint_angles[LegName.BR][JointName.KNEE])      

    def process_aux(self):
        """
        Check for commands and send latest status data to Auxiliary Board.
        """

        message = AuxMessage()
        message.joint_angle_error = self.motion.get_quad().get_joint_angle_error()
        message.inverse_kinematics_error = self.motion.get_quad().get_ik_error()
        message.joystick_error = self.input.gamepad.is_connected() == False
        message.can_error = self.motors.is_can_error()
        message.imuError = False

        voltage_accumulator: float = 0.0
        motors: Dict[str, Motor] = self.motors.get_all_motors()
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
        message.gamepad_battery_percent = self.input.gamepad.get_battery_life_percent()
        self.aux.send_at_rate(message.pack())
        self.aux.check_for_commands()

    def forward_states(self):
        system_status = SystemStatus()
        system_status.opMode.state = self.op_mode

        system_status.motion.state = self.motion.get_motion_state()
        system_status.target_motion.state = self.motion.get_target_motion_state()
        system_status.gait.state = self.motion.get_gait()     
        system_status.ik.status = Status.ERROR if self.motion.get_quad().get_ik_error() else Status.NONE
        system_status.joint_angle.status = Status.ERROR if self.motion.get_quad().get_joint_angle_error() else Status.NONE
        system_status.input.state = self.input.get_input_mode()
        system_status.loopTimes.main = self.main_loop_completion_time_ms
        system_status.loopTimes.motion = self.motion.get_loop_time_ms()
        system_status.loopTimes.can0 = self.motors.get_can_loop_time("can0")
        system_status.loopTimes.can1 = self.motors.get_can_loop_time("can1")

        system_status.motor.status = self.motors.get_status()
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
        self.forwarder.set_system_status(system_status)
        # self.forwarder.set_contacts(self.hardware.get_contacts())
        self.forwarder.set_motors_states(self.motors.get_all_motor_states())

        trajectories, rings, transitions, hold_trajectories = self.motion.get_trajectories()
        self.forwarder.set_trajectories(trajectories)
        self.forwarder.set_rings(rings)
        self.forwarder.set_transitions(transitions)
        self.forwarder.set_hold_trajectories(hold_trajectories)

        self.forwarder.set_ik_parameters(self.input.get_ik_parameters())

        # Get joint angles from physical quadruped.
        leg_angles: Dict[LegName, List[float]] = {}
        leg_angles[LegName.FL] = [
            self.motors.get_motor_position(MotorName.FLA),
            self.motors.get_motor_position(MotorName.FLH),
            self.motors.get_motor_position(MotorName.FLK),
        ]
        leg_angles[LegName.FR] = [
            self.motors.get_motor_position(MotorName.FRA),
            self.motors.get_motor_position(MotorName.FRH),
            self.motors.get_motor_position(MotorName.FRK),
        ]
        leg_angles[LegName.BL] = [
            self.motors.get_motor_position(MotorName.BLA),
            self.motors.get_motor_position(MotorName.BLH),
            self.motors.get_motor_position(MotorName.BLK),
        ]
        leg_angles[LegName.BR] = [
            self.motors.get_motor_position(MotorName.BRA),
            self.motors.get_motor_position(MotorName.BRH),
            self.motors.get_motor_position(MotorName.BRK),
        ]
        for leg, angles in leg_angles.items():
            leg_angles[leg] = [angle if angle is not None else 0.0 for angle in angles]
        live_quad = Quad()
        live_quad.set_joint_angles_degrees(leg_angles)
        self.forwarder.set_live_quad(live_quad)

    def sleep_loop(self):
        """
        Keep a consistance loop rate by sleeping the delta of processing time.
        Sleep required to share the CPU.
        """
        delta = time() - self.main_loop_time

        sleep_time = self.main_loop_rate_seconds - delta
        if sleep_time > 0:
            sleep(sleep_time)

        # if delta > self.main_loop_rate_ms:
        #    print(f"[Main] Warning, loop time exceeded tick rate! Loop time: {delta:0.3f}, tick rate: {self.main_loop_rate_ms:0.3f}")

        #print(f"[Loop] time to complete a loop: {delta:.3f}, sleep time: {sleep_time:.3f}")
        self.main_loop_completion_time_ms = (time() - self.main_loop_time) * 1000
        self.main_loop_time = time()

       

    ###############################################################################
    # Helpers
    ###############################################################################

    def clear_errors(self):
        print("[{MAIN}] clearing errors...")
        self.motors.clear_errors_all_motors()

    def shutdown(self, full_shutdown_flag: bool):
        print("[MAIN] shutdown...")

        # TODO: sit quadruped to avoid hard crashes

        # self.hardware.beep(BeepType.SHUTDOWN)

        self.motors.shutdown()
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
