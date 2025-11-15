#!/usr/bin/env python3
import os
import queue
import argparse
import traceback
from queue import Queue
from time import sleep, time
from rich import print  # Overrides print and injects colors
from typing import Dict, List

from quadruped.quad import Quad
from quadruped.gait_planner import Gait
from quadruped.interfaces import LegName, JointName, AngleUnits, MotionState
from quadruped.motion import Motion
from quadruped.interfaces import OpMode, Status
from quadruped.parameters.ik_parameters import IKParameters
from hardware.hardware import Hardware
from motors.motors import Motor, Motors
from motors.interfaces import MotorName, MotorSpeeds
from auxiliary.aux import Aux, AuxMessage, Sequence
from utilities.utilities import *
from utilities.wifi import Wifi
from utilities.service import ServiceCommand, service_action
from input.interfaces import InputCommand, InputMode
from input.gamepad import Gamepad
from input.touch import Touch
from input.input import Input
from status import SystemStatus
from forwarder import Forwarder


"""
    ElectroPup main application.
"""


class Main:
    def __init__(self, mode: OpMode):
        self.op_mode: OpMode = mode 

        print(f"[Main] starting in operation mode: {self.op_mode}")

        self.command_queue = Queue()

        self.wifi = Wifi()
        self.hardware = Hardware()      
        self.motion = Motion(op_mode=self.op_mode)
        self.forwarder = Forwarder()
        self.aux = Aux()
        self.gamepad = Gamepad(self.command_queue)
        self.touch = Touch(self.command_queue)

        self.main_loop_rate_seconds = 0.010
        self.main_loop_time: float = 0
        self.main_loop_completion_time_ms: float = 0

        self.battery_voltage: float = 0
        self.low_battery_voltage_threadhold: float = 19.8
        self.low_battery_alert_rate_seconds: float = 30
        self.low_battery_last_alert_time: float = time()

        self.input_mode: InputMode = InputMode.GAMEPAD
         
    ###############################################################################
    # Main Loop
    ###############################################################################

    def run(self):
        while True:

            self.get_commands()

            self.update_inputs()

            self.check_low_battery()

            self.process_aux()

            self.forward_states()

            self.sleep_loop()

    ###############################################################################
    # Loop Methods
    ###############################################################################

    def get_commands(self):
        command = None
        try:
            command = self.command_queue.get_nowait()
        except queue.Empty:
            pass

        if command is not None:
            self.process_command(command)
    
    
    def update_inputs(self):
        self.motion.set_ik_parameters(self.get_ik_parameters())
        self.motion.set_motion_parameters(self.get_motion_parameters())

    def check_low_battery(self):
        if self.battery_voltage > 0 and self.battery_voltage < self.low_battery_voltage_threadhold:
            if time() - self.low_battery_last_alert_time > self.low_battery_alert_rate_seconds:
                self.low_battery_last_alert_time = time()
                print("PLAY LOW", time())
                self.aux.play_sound(Sequence.LOW_BATTERY)

    def process_aux(self):
        """
        Check for commands and send latest status data to Auxiliary Board.
        """
        message = AuxMessage()
        message.joint_angle_error = self.motion.get_quad().get_joint_angle_error()
        message.inverse_kinematics_error = self.motion.get_quad().get_ik_error()
        message.joystick_error = self.gamepad.is_connected() == False
        message.can_error = self.motion.motors.is_can_error()
        message.imu_error = False
        message.low_battery = True if self.battery_voltage < self.low_battery_voltage_threadhold else False

        motors: Dict[str, Motor] = self.motion.motors.get_all_motors()
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

        message.battery_voltage = self.battery_voltage
        message.gamepad_battery_percent = self.gamepad.get_battery_life_percent()
        self.aux.send_at_rate(message.pack())
        self.aux.check_for_commands()

    def forward_states(self):
        system_status = SystemStatus()
        system_status.opMode.state = self.op_mode

        system_status.motion.state = self.motion.get_motion_state()
        system_status.target_motion.state = self.motion.get_target_motion_state()
        system_status.gait.state = self.motion.gait
        system_status.ik.status = Status.ERROR if self.motion.get_quad().get_ik_error() else Status.NONE
        system_status.joint_angle.status = Status.ERROR if self.motion.get_quad().get_joint_angle_error() else Status.NONE
        system_status.input.state = self.input_mode
        system_status.loopTimes.main = self.main_loop_completion_time_ms
        system_status.loopTimes.motion = self.motion.get_loop_time_ms()
        system_status.loopTimes.can0 = self.motion.motors.get_can_loop_time("can0")
        system_status.loopTimes.can1 = self.motion.motors.get_can_loop_time("can1")

        system_status.motor.status = self.motion.motors.get_status()
        # system_status.gpio.status = self.hardware.get_gpio_status()
        system_status.smbus.status = self.hardware.get_smbus_status()
        # system_status.power_sensor.status = self.hardware.get_power_sensor_status()
        system_status.imu.status = self.hardware.get_imu_status()
        system_status.imu.roll = self.hardware.get_imu_data().roll
        system_status.imu.pitch = self.hardware.get_imu_data().pitch
        system_status.can0.status = self.motion.motors.get_can_status("can0")
        system_status.can1.status = self.motion.motors.get_can_status("can1")
        system_status.gamepad.status = self.gamepad.get_status()
        system_status.gamepad.battery = self.gamepad.get_battery_life_str()

        voltage_accumulator: float = 0.0
        motors: Dict[str, Motor] = self.motion.motors.get_all_motors()
        for index, (motor_tag, motor) in enumerate(motors.items()):
            voltage_accumulator += motor.voltage
        self.battery_voltage = voltage_accumulator / len(motors)
        system_status.voltage.voltage = self.battery_voltage
        system_status.voltage.status = Status.ACTIVE if self.battery_voltage > 0 else Status.ERROR

        self.forwarder.set_sim_quad(self.motion.get_quad())
        self.forwarder.set_system_status(system_status)
        # self.forwarder.set_contacts(self.hardware.get_contacts())
        self.forwarder.set_motors_states(self.motion.motors.get_all_motor_states())

        trajectories, rings, transitions, hold_trajectories = self.motion.get_trajectories()
        self.forwarder.set_trajectories(trajectories)
        self.forwarder.set_rings(rings)
        self.forwarder.set_transitions(transitions)
        self.forwarder.set_hold_trajectories(hold_trajectories)

        self.forwarder.set_ik_parameters(self.get_ik_parameters())
        self.forwarder.set_motion_parameters(self.get_motion_parameters())

        # Get joint angles from physical quadruped.
        leg_angles: Dict[LegName, List[float]] = {}
        leg_angles[LegName.FL] = [
            self.motion.motors.get_motor_position(MotorName.FLA),
            self.motion.motors.get_motor_position(MotorName.FLH),
            self.motion.motors.get_motor_position(MotorName.FLK),
        ]
        leg_angles[LegName.FR] = [
            self.motion.motors.get_motor_position(MotorName.FRA),
            self.motion.motors.get_motor_position(MotorName.FRH),
            self.motion.motors.get_motor_position(MotorName.FRK),
        ]
        leg_angles[LegName.BL] = [
            self.motion.motors.get_motor_position(MotorName.BLA),
            self.motion.motors.get_motor_position(MotorName.BLH),
            self.motion.motors.get_motor_position(MotorName.BLK),
        ]
        leg_angles[LegName.BR] = [
            self.motion.motors.get_motor_position(MotorName.BRA),
            self.motion.motors.get_motor_position(MotorName.BRH),
            self.motion.motors.get_motor_position(MotorName.BRK),
        ]
        for leg, angles in leg_angles.items():
            leg_angles[leg] = [angle if angle is not None else 0.0 for angle in angles]
        live_quad = Quad()
        # live_quad.set_joint_angles_degrees(leg_angles)
        # live_quad.update_ht_body(self.input.get_ik_parameters())
        ik_parameters = IKParameters()
        ik_parameters.roll = self.hardware.get_imu_data().roll
        ik_parameters.pitch = self.hardware.get_imu_data().pitch
        live_quad.set_body_pose_by_transform_inputs(ik_parameters, live_quad.get_base_foot_points())
        live_quad.set_joint_angles_degrees(leg_angles)
        self.forwarder.set_live_quad(live_quad)

    def sleep_loop(self):
        """
        Keep a consistance loop rate by sleeping the delta of processing time.
        """
        delta = time() - self.main_loop_time

        sleep_time = self.main_loop_rate_seconds - delta
        if sleep_time > 0:
            sleep(sleep_time)

        # if delta > self.main_loop_rate_ms:
        #    print(f"[Main] Warning, loop time exceeded tick rate! Loop time: {delta:0.3f}, tick rate: {self.main_loop_rate_ms:0.3f}")

        # print(f"[Loop] time to complete a loop: {delta:.3f}, sleep time: {sleep_time:.3f}")
        self.main_loop_completion_time_ms = (time() - self.main_loop_time) * 1000
        self.main_loop_time = time()

    ###############################################################################
    # Helpers
    ###############################################################################
  
    def process_command(self, command: InputCommand):

        if command is InputCommand.SHUTDOWN:
            self.shutdown(full_shutdown_flag=True) 

        if command is InputCommand.WIFI_AS_CLIENT:
            self.aux.play_sound(Sequence.BTN_BEEP_SHORT)
            self.wifi.connect_to_wifi()  
            return  

        if command is InputCommand.WIFI_AS_HOTSPOT:
            self.aux.play_sound(Sequence.BTN_BEEP_SHORT)
            self.wifi.create_hotspot()    
            return

        if command is InputCommand.DISABLE_ENABLE_MOTORS:
            if self.op_mode is OpMode.LIVE:
                if self.motion.motors.is_motors_enabled():
                    self.motion.motors.disable_all_motors()
                    self.motion.set_target_motion_state(MotionState.STANDBY)
                else:
                    self.motion.motors.enable_all_motors()
            else:
                self.aux.play_sound(Sequence.ERROR)
                print(f"[Main] Warning, enable/disable motors blocked, LIVE operation mode not enabled.")

        if command is InputCommand.CLEAR_ERRORS:
            print(f"[Main] clearing errors...")
            self.motion.motors.clear_errors_all_motors()
            return

        if self.op_mode is OpMode.LIVE:
            if self.motion.get_motion_state() is MotionState.STANDBY:
                if not self.motion.motors.is_motors_enabled():
                    self.aux.play_sound(Sequence.ERROR)
                    print(f"[Main] Controller event {command.name} blocked, motors not enabled.")
                    return

        if command is InputCommand.STAND:
            self.motion.set_target_motion_state(MotionState.STAND)
            self.motor_enable_flag = True

        if command is InputCommand.SIT:
            self.motion.set_target_motion_state(MotionState.SIT)

        if command is InputCommand.POSE:
            self.motion.set_target_motion_state(MotionState.POSE)

        if command is InputCommand.WALK:
            self.motion.set_target_motion_state(MotionState.WALK)

        if command is InputCommand.GAIT_CRAWL:
            self.motion.set_target_gait(Gait.CRAWL)

        if command is InputCommand.GAIT_RUN:
            self.motion.set_target_gait(Gait.RUN)

        if command is InputCommand.GAIT_TROT:
            self.motion.set_target_gait(Gait.TROT)

        if command is InputCommand.GAIT_CLIMB:
            self.motion.set_target_gait(Gait.CLIMB)          

        print(f"[Main] Controller event received: {command.name}")
        self.aux.play_sound(Sequence.BTN_BEEP_SHORT)

    def get_motion_parameters(self):
        if self.input_mode is InputMode.GAMEPAD:
            return self.gamepad.get_motion_parameters()
        elif self.input_mode is InputMode.TOUCH:
            return self.touch.get_motion_parameters()

    def get_ik_parameters(self):
        if self.input_mode is InputMode.GAMEPAD:
            return self.gamepad.get_ik_parameters()
        elif self.input_mode is InputMode.TOUCH:
            return self.touch.get_ik_parameters()
    
    def shutdown(self, full_shutdown_flag=False):
        print(f"[Main] shutdown...")

        self.aux.play_sound(Sequence.SHUTDOWN)
        self.hardware.shutdown()
        self.gamepad.stop()
        self.touch.stop()
        self.motion.shutdown()
        self.forwarder.shutdown()

        if full_shutdown_flag:
            print(f"[Main] shutting down system...")
            sleep(1)
            os.system("sudo shutdown now")


###############################################################################
# Entry
###############################################################################
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run in live or development mode.")  
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--dev", action="store_true", help="Run in development mode")
    group.add_argument("-l", "--live", action="store_true", help="Run in live mode")
    group.add_argument("-s", "--service", action="store_true", help="Executed by the service")
    group.add_argument("--start", action="store_true", help="Start the service")
    group.add_argument("--stop", action="store_true", help="Stop the service")
    group.add_argument("--disable", action="store_true", help="Disable the service")
    group.add_argument("--restart", action="store_true", help="Restart the service")

    args = parser.parse_args()

    ###############################################################################
    # Process Arguments
    ###############################################################################

    if args.start:
        service_action(ServiceCommand.START, "main.service")

    if args.stop:
        service_action(ServiceCommand.STOP, "main.service")

    if args.disable:
        service_action(ServiceCommand.DISABLE, "main.service")

    if args.restart:
        service_action(ServiceCommand.RESET, "main.service")

    if args.dev:
        mode = OpMode.DEV
    elif args.live or args.service:
        mode = OpMode.LIVE
 
    if args.service == False:
        if is_service_running("main.service"):
            print(f"[Main] error, main.service is running, unable to start main.py")
            exit(1)

    ###############################################################################
    # Run Main Program
    ###############################################################################
  
    main = Main(mode=mode)

    try:
        main.run()
    except KeyboardInterrupt:
        print("Keyboard interrupt, exiting")
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
    finally:
        main.shutdown()
