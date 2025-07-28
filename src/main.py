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

# Local source.

from system.quadruped.quad import Quad
from system.input.input import Input
from system.quadruped.motion import Motion
from system.quadruped.parameters.frame_parameters import FrameParameters
from system.quadruped.parameters.motion_parameters import MotionParameters
from system.quadruped.parameters.ik_parameters import IKParameters
from system.motors.motors import Motor, Motors
from system.auxiliary.aux import Aux, StatusMessage
from system.utilities.utilities import *

from system.interfaces import SystemStates, OpModes, MotorSpeeds, MotorCurrents, Status, InputCommand, MotionStates
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

        self.input = Input(callback=self.controller_event_callback)

        self.motion = Motion()

        self.forwarder = Forwarder()

        self.quad_sim = Quad()
        self.quad_live = Quad()

        ######################################################################

        """   
        self.aux = Aux() 
        self.aux_send_rate_seconds : float = 0.125

        self.gamepad = Gamepad(self.motion_parameters)
        self.gamepad.register_controller_event_callback(self.controller_event_callback)
        self.gamepad_last_connected_time : float = 0
        self.gamepad_no_comms_timeout_seconds : float = 5
        
        self.gamepad_last_battery_check_time : float = 0
        self.gamepad_battery_check_rate_seconds : float = 1

        self.body = Body()       

        self.kinetic_state : KineticState = KineticState.STARTUP
        self.previous_kinetic_state : KineticState = KineticState.INIT 
        self.body_error_state : Body.ErrorState = Body.ErrorState.NONE
        self.speed : int = 0
        self.loop_time : float = 0
        
        #self.pose_start_time : float = 0
        #self.pose_timeout_seconds : float = 0
        """

        ######################################################################

        self.ik_status = Status.STANDBY
        self.joint_angle_status = Status.STANDBY

        self.main_loop_rate_ms = 0.020
        self.loop_time: float = 0
        self.loop_completion_time_ms: float = 0

        self.previous_system_state: SystemStates = SystemStates.INIT
        if self.op_mode == OpModes.LIVE:
            self.system_state: SystemStates = SystemStates.STANDBY
        elif self.op_mode == OpModes.SIM:
            self.system_state: SystemStates = SystemStates.MOTION

    ###############################################################################
    # Callback from Input(s)
    ###############################################################################

    def controller_event_callback(self, event: InputCommand):
        print(f"[MAIN] Controller event received: {event.name}")

        if event == InputCommand.STAND:
            if self.system_state is SystemStates.STANDBY:
                if self.hardware.get_motors_power_status() is Status.STANDBY:
                    self.system_state = SystemStates.POWER_ON_MOTORS
                else:
                    self.system_state = SystemStates.STAND

        if event == InputCommand.SIT:
            if self.hardware.get_motors_power_status() is Status.ACTIVE:
                self.system_state = SystemStates.SIT

        if event == InputCommand.CLEAR_MOTOR_ERRORS:
            self.clear_all_errors()

        if event == InputCommand.POSE:
            self.motion.set_target_motion_state(MotionStates.POSE)

        if event == InputCommand.BIAS_WALK:
            self.motion.set_target_motion_state(MotionStates.BIAS_WALK)

        if event == InputCommand.ROTATE:
            self.motion.set_target_motion_state(MotionStates.ROTATE)

        if event == InputCommand.VECTOR_WALK:
            self.motion.set_target_motion_state(MotionStates.VECTOR_WALK)

    ###############################################################################
    # Main Loop
    ###############################################################################

    def run(self):
        while True:

            self.process_state_changes()

            self.process_states()

            # self.check_motor_errors()

            # self.process_aux()

            self.forward_states()

            self.sleep_loop()

    ###############################################################################
    # Loop Methods
    ###############################################################################

    def process_state_changes(self):
        """
        Execute once after kinetic state change
        """

        if self.previous_system_state != self.system_state:
            self.previous_system_state = self.system_state
            print(f"[STATE] kinetic state changed to: {self.system_state.name}")

            if self.system_state == SystemStates.ERROR:
                pass

            elif self.system_state == SystemStates.STANDBY:
                pass

            elif self.system_state == SystemStates.ENABLE_MOTORS:
                pass

            elif self.system_state == SystemStates.STAND:
                self.speed = 500
                self.apply_controller_input(self.motion_parameters.get_pose_standing())
                self.motor_interface_front.enable_all_motors()
                self.motor_interface_back.enable_all_motors()

            elif self.system_state == SystemStates.SIT:
                self.speed = 500
                self.apply_controller_input(self.motion_parameters.get_pose_lie_down())

            elif self.system_state == SystemStates.MOTION:
                self.motion.set_target_motion_state(MotionStates.BIAS_WALK)

            elif self.system_state == SystemStates.POWER_DOWN:
                pass

    def process_states(self):
        """
        Kinetic state machine
        """
        if self.system_state == SystemStates.ERROR:
            pass

        elif self.system_state == SystemStates.STANDBY:
            pass

        elif self.system_state == SystemStates.ENABLE_MOTORS:
            pass

        elif self.system_state == SystemStates.STAND:
            if self.motor_interface_front.is_all_motor_angles_within_range(0.5):
                self.system_state = SystemStates.POSE

        elif self.system_state == SystemStates.SIT:
            if self.motor_interface_front.is_all_motor_angles_within_range(0.5):
                self.system_state = SystemStates.HALT

        elif self.system_state == SystemStates.MOTION:
            self.compute_quad()

        elif self.system_state == SystemStates.POWER_DOWN:
            pass

    def check_motor_errors(self):
        if self.motors.is_error():
            self.system_state = SystemStates.ERROR

    def process_aux(self):
        """
        Check for commands and send latest status data to Auxiliary Board.
        """

        self.aux.check_for_commands()

        message = StatusMessage()

        message.joint_angle_error = self.body_error_state == Quad.ErrorState.JOINT
        message.inverse_kinematics_error = self.body_error_state == Quad.ErrorState.KINEMATICS
        message.joystick_error = self.gamepad.is_connected() == False
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
        system_status.system.state = self.system_state

        system_status.motion.state = self.motion.get_motion_state()
        system_status.target_motion.state = self.motion.get_target_motion_state()
        #system_status.ik.status = self.ik_status
        #system_status.joint_angle.status = self.joint_angle_status
        system_status.gait.state = self.motion.get_gait()
        system_status.input.state = self.input.get_input_mode()
        #system_status.loopTimes.mainLoop = self.loop_completion_time_ms
        #system_status.loopTimes.can0 = self.motors.get_can_loop_time("can0")
        #system_status.loopTimes.can1 = self.motors.get_can_loop_time("can1")

        #system_status.gpio.status = self.hardware.get_gpio_status()
        #system_status.smbus.status = self.hardware.get_smbus_status()
        #ystem_status.power_sensor.status = self.hardware.get_power_sensor_status()
        #system_status.imu.status = self.hardware.get_imu_status()
        #system_status.imu.roll = self.hardware.get_imu_data().roll
        #system_status.imu.pitch = self.hardware.get_imu_data().pitch
        #system_status.expander.status = self.hardware.get_port_expander_status()
        #system_status.can0.status = self.motors.get_can_status("can0")
        #system_status.can1.status = self.motors.get_can_status("can1")
        system_status.gamepad.status = self.input.gamepad.get_status()
        system_status.gamepad.battery = self.input.gamepad.get_battery_life_str()

 
        self.forwarder.set_sim_quad(self.quad_sim)
        # self.forwarder.set_live_quad(self.quad_live)
        self.forwarder.set_system_status(system_status)
        # self.forwarder.set_contacts(self.hardware.get_contacts())
        # self.forwarder.set_motors_states(self.motors.get_all_motor_states())
        self.forwarder.set_trajectories(self.motion.get_trajectories())
        self.forwarder.set_soft_trajectories(self.motion.get_soft_trajectories())
        self.forwarder.set_rings(self.motion.get_visual_rings())
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

        if delta > self.main_loop_rate_ms:
            print(f"[MAIN] Warning, loop time exceeded tick rate! Loop time: {delta:0.3f}, tick rate: {self.main_loop_rate_ms:0.3f}")

        # print(f"[Loop] time to complete a loop: {delta:.3f}, sleep time: {sleep_time:.3f}")
        self.loop_completion_time_ms = delta * 1000
        self.loop_time = time.time()

    ###############################################################################
    # Other Methods (called by loop methods)
    ###############################################################################

    def stand_quad(self):
        self.stand.tick()

    def compute_quad(self):
        motion_parameters = self.input.get_motion_parameters()
        ik_parameters = self.input.get_ik_parameters()

        self.motion.tick(self.quad_sim, ik_parameters, motion_parameters)  
        self.body_error_state = self.quad_sim.set_body_pose_by_transform_inputs(ik_parameters)

        return

        if self.body_error_state == Quad.ErrorState.NONE:
            joint_angles = self.quad_sim.get_joint_angles(units="DEGREES")
            # APPLY JOINT ANGLES
        elif self.body_error_state == Quad.ErrorState.KINEMATICS or self.body_error_state == Quad.ErrorState.JOINT:
            print(f"[Body] error, {self.body_error_state.name}")

        """try:
            motion_parameters = self.input.get_motion_parameters()
            ik_parameters = self.input.get_ik_parameters()
            #self.motion.tick(self.sim_hexapod, ik_parameters, motion_parameters)
            self.ik_status = Status.ACTIVE
            self.joint_angle_status = Status.ACTIVE
        except OutOfBounds:
            self.joint_angle_status = Status.ERROR
        except (
            CoxiaInterceptsGround,
            UnableToReachGround,
            FootPenetratesGround,
        ) as e:
            self.ik_status = Status.ERROR
            print(f"{time.time()} {e}")
            traceback.print_exc()
            return"""

        # Apply angles to motors.
        """leg_angles = self.sim_hexapod.get_all_leg_angles_radians()
        for key, leg_angle in leg_angles.items():
            self.motors.set_target_position(key, leg_angle)"""

    ###############################################################################
    # Helpers
    ###############################################################################

    def clear_all_errors(self):
        self.body_error_state = Quad.ErrorState.NONE
        self.motor_interface_front.clear_errors_all_motors()
        self.motor_interface_back.clear_errors_all_motors()
        self.kinetic_state = KineticState.STARTUP

    def shutdown(self, full_shutdown_flag: bool):
        print("[MAIN] shutdown...")

        # TODO: sit hexapod to avoid hard crashes

        # self.hardware.beep(BeepType.SHUTDOWN)
        # self.motors.shutdown()
        # self.hardware.power_motors_off()
        # self.hardware.shutdown()
        # self.input.shutdown()
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
