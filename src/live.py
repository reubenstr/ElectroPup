#!/usr/bin/env python3

"""
    ElectroPup main application to control the physical quadruped with live input from the gamepad.
"""

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
from system.parameters.frame_parameters import FrameParameters
from system.parameters.motion_parameters import MotionParameters, KineticState, ControllerEvent
from system.motors.motors import Motor, Motors
from system.auxiliary.aux import Aux, StatusMessage
from system.utilities import *


class Live():
    def __init__(self):
        motion_parameters_filepath = "./system/parameters/motion_parameters.yaml"
        frame_parameters_filepath = "./system/parameters/frame_parameters.yaml"

        frame_parameters = FrameParameters(frame_parameters_filepath)
        self.motion_parameters = MotionParameters(motion_parameters_filepath)

        self.aux = Aux() 
        self.aux_send_rate_seconds : float = 0.125

        self.gamepad = Gamepad(self.motion_parameters)
        self.gamepad.register_controller_event_callback(self.controller_event_callback)
        self.gamepad_last_connected_time : float = 0
        self.gamepad_no_comms_timeout_seconds : float = 5
        
        self.gamepad_last_battery_check_time : float = 0
        self.gamepad_battery_check_rate_seconds : float = 1

        self.body = Body(frame_parameters=frame_parameters)

        motor_tags = ["FLA", "FLH", "FLK", "FRA", "FRH", "FRK"] 
        self.motor_interface_front = Motors(can_bus_id="can0", motor_tags=motor_tags)
        self.motor_interface_front.cmd_all_motors_off()                
        self.motor_interface_front.set_limits("FLA", degrees(frame_parameters.abduction_joint_lower_bounds), degrees(frame_parameters.abduction_joint_upper_bounds))
        self.motor_interface_front.set_limits("FLH", degrees(frame_parameters.hip_joint_lower_bounds), degrees(frame_parameters.hip_joint_upper_bounds))
        self.motor_interface_front.set_limits("FLK", degrees(frame_parameters.knee_joint_lower_bounds), degrees(frame_parameters.knee_joint_upper_bounds))               
        self.motor_interface_front.set_limits("FRA", degrees(frame_parameters.abduction_joint_lower_bounds), degrees(frame_parameters.abduction_joint_upper_bounds))
        self.motor_interface_front.set_limits("FRH", degrees(frame_parameters.hip_joint_lower_bounds), degrees(frame_parameters.hip_joint_upper_bounds))
        self.motor_interface_front.set_limits("FRK", degrees(frame_parameters.knee_joint_lower_bounds), degrees(frame_parameters.knee_joint_upper_bounds))

        motor_tags_back = ["BLA", "BLH", "BLK", "BRA", "BRH", "BRK"]
        self.motor_interface_back = Motors(can_bus_id="can1", motor_tags=motor_tags_back)  
        self.motor_interface_back.cmd_all_motors_off()               
        self.motor_interface_back.set_limits("BLA", degrees(frame_parameters.abduction_joint_lower_bounds), degrees(frame_parameters.abduction_joint_upper_bounds))
        self.motor_interface_back.set_limits("BLH", degrees(frame_parameters.hip_joint_lower_bounds), degrees(frame_parameters.hip_joint_upper_bounds))
        self.motor_interface_back.set_limits("BLK", degrees(frame_parameters.knee_joint_lower_bounds), degrees(frame_parameters.knee_joint_upper_bounds))               
        self.motor_interface_back.set_limits("BRA", degrees(frame_parameters.abduction_joint_lower_bounds), degrees(frame_parameters.abduction_joint_upper_bounds))
        self.motor_interface_back.set_limits("BRH", degrees(frame_parameters.hip_joint_lower_bounds), degrees(frame_parameters.hip_joint_upper_bounds))
        self.motor_interface_back.set_limits("BRK", degrees(frame_parameters.knee_joint_lower_bounds), degrees(frame_parameters.knee_joint_upper_bounds))
            
        self.kinetic_state : KineticState = KineticState.STARTUP
        self.previous_kinetic_state : KineticState = KineticState.INIT 
        self.body_error_state : Body.ErrorState = Body.ErrorState.NONE
        self.speed : int = 0
        self.loop_time : float = 0
        
        #self.pose_start_time : float = 0
        #self.pose_timeout_seconds : float = 0
        
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
            self.motor_interface_front.set_motor_targets(motor_tag="FLA", speed=self.speed, angle=-joint_angles['front_left']['abduction'])   
            self.motor_interface_front.set_motor_targets(motor_tag="FLH", speed=self.speed, angle=joint_angles['front_left']['hip'])  
            self.motor_interface_front.set_motor_targets(motor_tag="FLK", speed=self.speed, angle=joint_angles['front_left']['knee']) 
            self.motor_interface_front.set_motor_targets(motor_tag="FRA", speed=self.speed, angle=joint_angles['front_right']['abduction'])   
            self.motor_interface_front.set_motor_targets(motor_tag="FRH", speed=self.speed, angle=joint_angles['front_right']['hip'])  
            self.motor_interface_front.set_motor_targets(motor_tag="FRK", speed=self.speed, angle=joint_angles['front_right']['knee']) 
            self.motor_interface_back.set_motor_targets(motor_tag="BLA", speed=self.speed, angle=-joint_angles['back_right']['abduction'])   
            self.motor_interface_back.set_motor_targets(motor_tag="BLH", speed=self.speed, angle=joint_angles['back_left']['hip'])  
            self.motor_interface_back.set_motor_targets(motor_tag="BLK", speed=self.speed, angle=joint_angles['back_left']['knee']) 
            self.motor_interface_back.set_motor_targets(motor_tag="BRA", speed=self.speed, angle=joint_angles['back_left']['abduction'])   
            self.motor_interface_back.set_motor_targets(motor_tag="BRH", speed=self.speed, angle=joint_angles['back_right']['hip'])  
            self.motor_interface_back.set_motor_targets(motor_tag="BRK", speed=self.speed, angle=joint_angles['back_right']['knee']) 
        
        elif self.body_error_state == Body.ErrorState.KINEMATICS or self.body_error_state == Body.ErrorState.JOINT:
            print(f"[Body] error, {self.body_error_state.name}")
                          
                
    ###############################################################################
    # Main Loop
    ###############################################################################       
        
    def run(self):
        while True:        
            
            self.process_state_changes()
            
            self.process_states()
            
            self.check_motor_errors()
                    
            self.process_aux()
            
            self.check_game_pad()                        

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
                self.motor_interface_front.cmd_all_motors_off()
                self.motor_interface_back.cmd_all_motors_off()    
            
            elif self.kinetic_state == KineticState.STARTUP:              
                self.motor_interface_front.start()
                self.motor_interface_back.start()                    
            
            elif self.kinetic_state == KineticState.HALT:
                self.motor_interface_front.cmd_all_motors_off()
                self.motor_interface_back.cmd_all_motors_off()
            
            elif self.kinetic_state == KineticState.STAND: 
                self.speed = 500   
                self.apply_controller_input(self.motion_parameters.get_pose_standing())                      
                self.motor_interface_front.cmd_all_motors_on()
                self.motor_interface_back.cmd_all_motors_on()   
                
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
            if self.motor_interface_front.op_is_all_motor_angles_within_range(0.5):
                self.kinetic_state = KineticState.POSE
                
        elif self.kinetic_state == KineticState.LIE_DOWN:                       
            if self.motor_interface_front.op_is_all_motor_angles_within_range(0.5):
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
            message.motor_ons[index] = motor.is_on()
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
                      
    
    def sleep_loop(self):
        """
        Keep a consistance loop rate by sleeping the delta of processing time.
        Sleep required to share the CPU.
        """
        delta = time.time() - self.loop_time          
          
        sleep_time = 0.010 - delta
        if sleep_time > 0:    
            sleep(sleep_time)
        
        #print(f"[Loop] time to complete a loop: {delta:.3f}, sleep time: {sleep_time:.3f}")                            
        self.loop_time = time.time()     
        
    ###############################################################################
    # Helpers
    ###############################################################################  
                
    def clear_all_errors(self):    
        self.body_error_state = Body.ErrorState.NONE
        self.motor_interface_front.cmd_all_motors_clear_errors()           
        self.motor_interface_back.cmd_all_motors_clear_errors() 
        self.kinetic_state = KineticState.STARTUP
                                        
    def shutdown(self):
        self.motor_interface_front.shutdown()
        self.gamepad.disconnect()
        
                
###############################################################################
# Entry
###############################################################################
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the physical quadruped live on the Raspberry Pi")
    parser.add_argument('-r', '--reset', action='store_true', help='Restart the live.service')
    
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
    
    ###############################################################################
    # Run Main Program
    ###############################################################################
    
    if is_service_running("live.service"):
        print(f"[Live] error, live.service is running, unable to start live.py")
        exit(1)
        
    live = Live()    
          
    try:        
        live.run()            
    except KeyboardInterrupt:
        print ('Keyboard interrupt, exiting')        
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())        
    finally:          
        live.shutdown()