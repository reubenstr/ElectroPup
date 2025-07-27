#!/usr/bin/env python3

"""
    ElectroPup main application to control the physical quadruped with live input from the gamepad.
"""

import os
import time
import argparse
import traceback
import subprocess
from math import pi
from time import sleep
from rich import print # Overrides print and injects colors
from math import degrees
from typing import List, Dict

# Local source.

from system.quadruped.body import Body
from system.gamepad.gamepad import Gamepad
from system.quadruped.parameters.frame_parameters import FrameParameters
from system.quadruped.parameters.motion_parameters import MotionParameters, KineticState, ControllerEvent
from system.motors.motors import Motor, Motors
from system.auxiliary.aux import Aux, StatusMessage
from system.utilities.utilities import *

from system.interfaces import SystemStates, OpModes, MotorSpeeds, MotorCurrents, Status, InputCommand
from system.status import SystemStatus
from system.forwarder import Forwarder


class Main():
    def __init__(self, mode: OpModes):
        self.op_mode: OpModes = mode

        print(f"[MAIN] starting in operation mode: {self.op_mode}")

        allow_enable = True if self.op_mode == OpModes.LIVE else False


        self.forwarder = Forwarder()


        self.sim_quad= Body()  
        self.live_quad = Body() 

        ######################################################################
           
        '''   
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
        '''

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
    # Methods
    ###############################################################################   
        
    def controller_event_callback(self, event : ControllerEvent):    
        print(f"[EVENT] controller event received: {event.name}")
        
        if event == ControllerEvent.KINETIC_STATE_TOGGLE:        
            if self.kinetic_state == KineticState.POSE:
                self.kinetic_state = KineticState.MOTION
            elif self.kinetic_state == KineticState.MOTION:
                self.kinetic_state = KineticState.POSE 
        elif event == ControllerEvent.MOTOR_POWER_TOGGLE: 
            if self.kinetic_state == KineticState.HALT or self.kinetic_state == KineticState.STARTUP: 
                self.kinetic_state = KineticState.STAND 
            elif self.kinetic_state != KineticState.ERROR: 
                self.kinetic_state = KineticState.HALT                    
        elif event == ControllerEvent.MOTOR_CLEAR_ERRORS:
            self.clear_all_errors()
        elif event == ControllerEvent.LIE_DOWN_AND_MOTORS_OFF:
            if self.kinetic_state == KineticState.POSE or self.kinetic_state == KineticState.MOTION:
                self.kinetic_state = KineticState.LIE_DOWN
            
                              
    def apply_controller_input(self, motion_parameters : MotionParameters):  
        self.body_error_state = self.body.set_body_pose_by_transform_inputs(
            phi=motion_parameters.roll,
            theta=motion_parameters.pitch,
            psi=motion_parameters.yaw,
            x=motion_parameters.side_translation,
            y=motion_parameters.height_translation,
            z=motion_parameters.forward_translation,
        ) 
               
        if self.body_error_state == Body.ErrorState.NONE:  
            joint_angles = self.body.get_joint_angles(units="DEGREES") 
            self.motor_interface_front.set_motor_targets(motor_name="FLA", speed=self.speed, position=-joint_angles['front_left']['abduction'])   
            self.motor_interface_front.set_motor_targets(motor_name="FLH", speed=self.speed, position=joint_angles['front_left']['hip'])  
            self.motor_interface_front.set_motor_targets(motor_name="FLK", speed=self.speed, position=joint_angles['front_left']['knee']) 
            self.motor_interface_front.set_motor_targets(motor_name="FRA", speed=self.speed, position=joint_angles['front_right']['abduction'])   
            self.motor_interface_front.set_motor_targets(motor_name="FRH", speed=self.speed, position=joint_angles['front_right']['hip'])  
            self.motor_interface_front.set_motor_targets(motor_name="FRK", speed=self.speed, position=joint_angles['front_right']['knee']) 
            self.motor_interface_back.set_motor_targets(motor_name="BLA", speed=self.speed, position=-joint_angles['back_right']['abduction'])   
            self.motor_interface_back.set_motor_targets(motor_name="BLH", speed=self.speed, position=joint_angles['back_left']['hip'])  
            self.motor_interface_back.set_motor_targets(motor_name="BLK", speed=self.speed, position=joint_angles['back_left']['knee']) 
            self.motor_interface_back.set_motor_targets(motor_name="BRA", speed=self.speed, position=joint_angles['back_left']['abduction'])   
            self.motor_interface_back.set_motor_targets(motor_name="BRH", speed=self.speed, position=joint_angles['back_right']['hip'])  
            self.motor_interface_back.set_motor_targets(motor_name="BRK", speed=self.speed, position=joint_angles['back_right']['knee']) 
        
        elif self.body_error_state == Body.ErrorState.KINEMATICS or self.body_error_state == Body.ErrorState.JOINT:
            print(f"[Body] error, {self.body_error_state.name}")
                          
                
    ###############################################################################
    # Main Loop
    ###############################################################################       
        
    def run(self):
        while True:        
            
            #self.process_state_changes()
            
            #self.process_states()
            
            #self.check_motor_errors()
                    
            #self.process_aux()
            
            #self.check_game_pad() 

            self.forward_states()                       

            self.sleep_loop()           
            
    ###############################################################################
    # Loop Methods
    ###############################################################################   
       
    def process_state_changes(self):                                
        """Execute once after kinetic state change""" 
                           
        if self.previous_kinetic_state != self.kinetic_state:   
            self.previous_kinetic_state = self.kinetic_state
            print(f"[STATE] kinetic state changed to: {self.kinetic_state.name}")
            
            self.gamepad.set_kinetic_state(self.kinetic_state)  
                            
            if self.kinetic_state == KineticState.ERROR:
                self.motor_interface_front.disable_all_motors()
                self.motor_interface_back.disable_all_motors()    
            
            elif self.kinetic_state == KineticState.STARTUP:              
                self.motor_interface_front.start()
                self.motor_interface_back.start()                    
            
            elif self.kinetic_state == KineticState.HALT:
                self.motor_interface_front.disable_all_motors()
                self.motor_interface_back.disable_all_motors()
            
            elif self.kinetic_state == KineticState.STAND: 
                self.speed = 500   
                self.apply_controller_input(self.motion_parameters.get_pose_standing())                      
                self.motor_interface_front.enable_all_motors()
                self.motor_interface_back.enable_all_motors()   
                
            elif self.kinetic_state == KineticState.LIE_DOWN: 
                self.speed = 500   
                self.apply_controller_input(self.motion_parameters.get_pose_lie_down())                      
                                                
            elif self.kinetic_state == KineticState.POSE:
                self.speed = 2000   
                                    
            elif self.kinetic_state == KineticState.MOTION:
                self.speed = 1000
                    
            elif self.kinetic_state == KineticState.FLIP:
                    pass  
    
    def process_states(self):
        """Kinetic state machine"""      
        if self.kinetic_state == KineticState.ERROR:
            pass
        
        elif self.kinetic_state == KineticState.HALT:
            pass
        
        elif self.kinetic_state == KineticState.STAND:                       
            if self.motor_interface_front.is_all_motor_angles_within_range(0.5):
                self.kinetic_state = KineticState.POSE
                
        elif self.kinetic_state == KineticState.LIE_DOWN:                       
            if self.motor_interface_front.is_all_motor_angles_within_range(0.5):
                self.kinetic_state = KineticState.HALT        
        
        elif self.kinetic_state == KineticState.POSE:    
            motion_parameters = self.gamepad.get_motion_parameters()            
            self.apply_controller_input(motion_parameters)  
        
        elif self.kinetic_state == KineticState.MOTION:               
            motion_parameters = self.gamepad.get_motion_parameters()            
            self.apply_controller_input(motion_parameters)              
        
        elif self.kinetic_state == KineticState.FLIP:
            pass   
        
        
    def check_motor_errors(self): 
        if self.motor_interface_front.is_error() or self.motor_interface_back.is_error(): 
            self.kinetic_state = KineticState.ERROR    
       
    def process_aux(self):
        """
        Check for commands and send latest status data to Auxiliary Board.
        """
        
        self.aux.check_for_commands()
        
        message = StatusMessage()  
        
        message.joint_angle_error = self.body_error_state ==  Body.ErrorState.JOINT
        message.inverse_kinematics_error = self.body_error_state ==  Body.ErrorState.KINEMATICS
        message.joystick_error = self.gamepad.is_connected() == False
        message.can_error = self.motor_interface_front.is_can_error() or self.motor_interface_back.is_can_error()
        message.imuError = False
              
        voltage_accumulator : float = 0.0
        motors : Dict[str, Motor] = self.motor_interface_front.get_all_motors() | self.motor_interface_back.get_all_motors()
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
        
    
    def check_game_pad(self):
        if self.gamepad.is_connected():
            self.gamepad_last_connected_time = time.time()                      
        else:        
            if time.time() - self.gamepad_last_connected_time > self.gamepad_no_comms_timeout_seconds:
                if self.kinetic_state == KineticState.POSE or self.kinetic_state == KineticState.MOTION:
                    self.kinetic_state = KineticState.LIE_DOWN
                      
    
    def forward_states(self):
        system_status = SystemStatus()
        system_status.opMode.state = self.op_mode
        system_status.system.state = self.system_state
        

        self.forwarder.set_sim_quad(self.sim_quad)
        self.forwarder.set_live_quad(self.live_quad)

    
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
    # Helpers
    ###############################################################################  
                
    def clear_all_errors(self):    
        self.body_error_state = Body.ErrorState.NONE
        self.motor_interface_front.clear_errors_all_motors()           
        self.motor_interface_back.clear_errors_all_motors() 
        self.kinetic_state = KineticState.STARTUP
                                        
 
    def shutdown(self, full_shutdown_flag: bool):
        print("[MAIN] shutdown...")

        # TODO: sit hexapod to avoid hard crashes

        #self.hardware.beep(BeepType.SHUTDOWN)
        #self.motors.shutdown()
        #self.hardware.power_motors_off()
        #self.hardware.shutdown()
        #self.input.shutdown()
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
    parser.add_argument('-r', '--reset', action='store_true', help='Restart the service')
    args = parser.parse_args()


    
    ###############################################################################
    # Process Arguments
    ###############################################################################
    
    if args.reset:
        try:
            subprocess.run(['sudo', 'systemctl', 'restart', 'live.service'], check=True)
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
        print ('Keyboard interrupt, exiting')        
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())        
    finally:          
        main.shutdown(full_shutdown_flag=False)