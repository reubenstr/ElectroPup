#!/usr/bin/python3

"""
    Controls a collection of MG4010E-i10v3 actuators on a single CAN bus network.
    
    Class expects the hardware ID of the actuators to be [1 to number_of_motors]

    Creates a constains stream of target (angle, speed) updates via a thread.
    
    Application should poll for errors and take action such as shutting down the other motors.

    Actuator driver limitations:       
        - The driver does not have a min and max angle, therefore there is a higher risk of collision.
        - CAN is no able to set torque limit, speed limit, etc. Only the UART interface is capable
            of setting these parameters. The torque limit is used to create 'compliance'.  
            
            
    Motor startup angle reading is 0 to 360, but this library uses a -180 to 180 convention.
    If motors angles at startup are greater than 180 an offset flag is set and angles readings will be offset by -360.
          
               
"""

import os
import can
import sys
import time
import copy
import traceback
from time import sleep
import numpy as np
import random
from rich import print # Overrides print and injects colors
from threading import Thread, Event, Lock
from queue import Queue, Empty
from dataclasses import dataclass
from typing import Dict
from enum import Enum


# Local
from . can_interface import CanInterface


class Motor():
    def __init__(self,  tag : str, motor_id : int):
        self.tag = tag
        self.motor_id = motor_id   
                   
        # Targets:       
        self.target_speed: int = 100
        self.target_angle_degrees : float = 0
           
        # Motor states (from motor driver):
        self.temperature : int = 0
        self.voltage : float = 0               
        self.watts : float = 0
        self.motor_speed : int = 0
        self.encoder_position : int = 0
        self.angle_degrees : float = 0
        
        # Motor fault states (from motor driver):
        self.under_voltage_protection : bool = False
        self.over_voltage_protection  : bool = False
        self.over_temperature_protection : bool = False
        self.lost_input_protection : bool = False    
        
        # Motor fault states (from library):
        self.angle_limit_breached : bool = False
             
        # Communication states:
        self.reply_timeout_count : int = 0
        
        # Limits:
        self.angle_min : float = 0
        self.angle_max : float = 0
        
        # Misc.
        self.apply_negative_angle_offset : bool = False

class MotorDirection(Enum):  
    COUNTER_CLOCKWISE = 0
    CLOCKWISE = 1

class Motors(Thread):
    
    ###############################################################################
    # Class Initialization
    ###############################################################################
    
    def __init__(self, can_bus_id : str, motor_tags : list):
        Thread.__init__(self) 
        
        '''
        Parameters:
        - can_bus_id (str): the ID of the CAN bus, example CAN0, CAN1
        - motor_tags (str): list of tags as keys to access motor objects                      
        '''
        
        self.exit_event = Event()   
        self.lock = Lock()          
        self.comm_lock = Lock()  
        
        self.tag = can_bus_id.upper()
        
        self.motors : Dict[str, Motor] = {} 
        for i, tag in enumerate(motor_tags):
            self.motors[tag] = Motor(tag=tag, motor_id = i + 1)
    
        self.can_interface = CanInterface(can_bus_id)
        self.can_interface.op_can_init()
        
        # Timeouts and Timings:
        self.max_reply_timeouts_allow = 3
      
        # Control:
        self.motors_on : bool = False       
                
    ###############################################################################
    # Per Motor
    ###############################################################################      
 
    def cmd_motor_on(self, motor_tag : str):    
        start = time.time() 
        motor_id = self.motors[motor_tag].motor_id
        success = self.can_interface.cmd_motor_on(motor_id)          
        if success:
            print(f"[{self.tag}][{motor_tag}] command on completed, success: {success}, time: {time.time() - start:0.3f}")   
            self.motors[motor_tag].reply_timeout_count = 0 
        else:
            self.motors[motor_tag].reply_timeout_count += 1 
        return success      
              
    def cmd_motor_off(self, motor_tag: str) :    
        start = time.time() 
        motor_id = self.motors[motor_tag].motor_id
        success = self.can_interface.cmd_motor_off(motor_id)        
        if success:
            print(f"[{self.tag}][{motor_tag}] command off completed, success: {success}, time: {time.time() - start:0.3f}")   
            self.motors[motor_tag].reply_timeout_count = 0 
        else:
            self.motors[motor_tag].reply_timeout_count += 1 
        return success    
          
    def cmd_motor_set_zero_to_current_position(self, motor_tag: str):    
        start = time.time() 
        motor_id = self.motors[motor_tag].motor_id
        success = self.can_interface.cmd_set_zero_to_current_pos(motor_id)                
        if success:
            print(f"[{self.tag}][{motor_tag}] command set zero to current position completed, success: {success}, time: {time.time() - start:0.3f}")    
            self.motors[motor_tag].reply_timeout_count = 0 
        else:
            self.motors[motor_tag].reply_timeout_count += 1 
        return success        
    
    def op_motor_buzz(self, motor_tag: str, duration_seconds : int):
        """Vibrates motors used to assist assembly and debugging"""
        motor_id = self.motors[motor_tag].motor_id       
        print(f"[{self.tag}][{motor_tag}] buzzing motor {motor_tag} with ID {motor_id} for {duration_seconds} seconds")    
        start = time.time()        
        while time.time() - start < duration_seconds:            
            self.can_interface.cmd_motor_increment_angle(motor_id, speed=250, angle=1)
            sleep(0.250)
            self.can_interface.cmd_motor_increment_angle(motor_id, speed=250, angle=-1)
            sleep(0.250)
     
    def get_motor_tag_by_motor_id(self, motor_id : int):
            for key, motor in self.motors.items():
                if motor.motor_id == motor_id:
                    return key
            
    ###############################################################################
    # All Motors
    ###############################################################################      
               
    def cmd_all_motors_on(self):
        with self.comm_lock:
            self.motors_on = True
            success = True
            start = time.time()
            for motor in self.motors.values():            
                success = self.can_interface.cmd_motor_on(motor.motor_id)
                if not success:
                    success = False      
            print(f"[{self.tag}][ALL] command motors on completed, success: {success}, time: {time.time() - start:0.3f}")
            return success
                
    def cmd_all_motors_off(self):
        with self.comm_lock:
            self.motors_on = False
            success = True
            start = time.time()
            for motor in self.motors.values():
                success = self.can_interface.cmd_motor_off(motor.motor_id)
                if not success:
                    success = False       
            print(f"[{self.tag}][ALL] command motors off completed, success: {success}, time: {time.time() - start:0.3f}")
            return success
        
    def cmd_all_motors_clear_errors(self):
        with self.comm_lock:           
            success = True
            start = time.time()
            for motor_tag, motor in self.motors.items():
                self.motors[motor_tag].reply_timeout_count = 0
                success = self.can_interface.cmd_clear_motor_errors(motor.motor_id)
                if not success:
                    success = False       
            print(f"[{self.tag}][ALL] command clear errors completed, success: {success}, time: {time.time() - start:0.3f}")
            return success
                 
                
    ###############################################################################
    # Protected Getters, Setters, and Operations
    ###############################################################################
           
    def set_limits(self, motor_tag : str, angle_min : float, angle_max : float):
        with self.lock:
            self.motors[motor_tag].angle_min = angle_min
            self.motors[motor_tag].angle_max = angle_max
            
    def set_apply_negative_offset_angle_flag(self, motor_tag : str, value : bool):
        with self.lock:
            self.motors[motor_tag].apply_negative_angle_offset = value
                   
    def set_motor_targets(self, motor_tag : str, speed : int, angle : float):              
        with self.lock:
            self.motors[motor_tag].target_speed = speed
            self.motors[motor_tag].target_angle_degrees = angle
         
    def get_motor_targets(self,  motor_tag : str):      
        with self.lock:                    
            return self.motors[motor_tag].target_speed, self.motors[motor_tag].target_angle_degrees
        
    def get_motor(self, motor_tag : str):      
        with self.lock:                    
            return self.motors[motor_tag]
    
    def get_all_motors(self):      
        with self.lock:                    
            return self.motors.copy()
        
    def get_motor_angle(self, motor_tag : str):      
        with self.lock:                    
            return self.motors[motor_tag].angle_degrees
       
    def op_fetch_motor_angle(self, motor_tag : str):
        with self.lock: 
            motor_id = self.motors[motor_tag].motor_id
            sensor_angle = self.can_interface.req_motor_multi_angle(motor_id) 
            
            if self.motors[motor_tag].apply_negative_angle_offset:
                sensor_angle += -360.0
            
            if sensor_angle:
                self.motors[motor_tag].reply_timeout_count = 0 
                self.motors[motor_tag].angle_degrees = sensor_angle  
                return True
            else:
                self.motors[motor_tag].reply_timeout_count += 1     
                return False
                   
    def op_set_all_target_angles_to_current_angles(self):
        """
        Sets all motor target angles to current current.  
        """
        with self.lock: 
            for motor_tag, motor in self.motors.items(): 
                self.motors[motor_tag].target_angle_degrees = self.motors[motor_tag].angle_degrees                
        
    def op_is_all_motor_angles_within_range(self, tolerance : float): 
        with self.lock:
            for motor_tag, motor in self.motors.items():
                if self.is_angle_within_range(motor, tolerance) == False:
                    #print(motor_tag, motor.angle_degrees, motor.target_angle_degrees)
                    return False                    
            return True 
    
    def is_error(self) :
        """        
        Args: None          

        Returns:
            bool: True if motor contains a fault state or comms error
        """
        if self.can_interface.is_can_error():
            return True
        
        if not self.is_alive():
            return True    
        
        with self.lock: 
            error = False
            for motor_tag, motor in self.motors.items():
                if motor.angle_limit_breached:
                    error = True                
                if motor.under_voltage_protection or motor.over_voltage_protection or motor.over_temperature_protection or motor.lost_input_protection:                 
                    error = True
                if motor.reply_timeout_count > self.max_reply_timeouts_allow:
                    error = True
            return error      
                                  
                        
    ###############################################################################
    # Worker
    ###############################################################################
        
    def _worker_set_all_targets(self):
        """Send target speed and angle to the motors"""
        for motor_tag, motor in self.motors.items():   
            speed, angle = self.get_motor_targets (motor_tag)                        
            success = self.can_interface.cmd_motor_multi_angle_2(motor.motor_id, speed, angle)  
            if success:
                self.motors[motor_tag].reply_timeout_count = 0  
            else:
                self.motors[motor_tag].reply_timeout_count += 1     
    
    def _worker_get_all_angles(self): 
        success = True  
        for motor_tag, motor in self.motors.items():
            if self.op_fetch_motor_angle(motor_tag) == False:
                success = False    
        return success        
    
    def _worker_get_all_status(self):
        """Get motor status from the motors"""        
        for motor_tag, motor in self.motors.items():   
            result = self.can_interface.req_state_1(motor.motor_id)  
            if result:                          
                with self.lock:             
                    self.motors[motor_tag].temperature = result['temperature']
                    self.motors[motor_tag].voltage = result['voltage']
                    self.motors[motor_tag].under_voltage_protection = result['under_voltage_protection']  
                    self.motors[motor_tag].over_voltage_protection = result['over_voltage_protection']
                    self.motors[motor_tag].over_temperature_protection = result['over_temperature_protection']
                    self.motors[motor_tag].lost_input_protection = result['lost_input_protection']  
    
    def _worker_check_all_angle_limits(self)   :
        with self.lock:
            for motor_tag, motor in self.motors.items(): 
                if motor.angle_degrees < motor.angle_min or motor.angle_degrees > motor.angle_max:
                    self.motors[motor_tag].angle_limit_breached = True 
                    print(f"[{motor_tag}] error, breach! angle: {motor.angle_degrees}, min: {motor.angle_min}, max: {motor.angle_max}")

    
    def run(self):      
        """
        Main function that continously updates motor targets (speed, position) and checks for errors.
        """  
       
        if self._worker_get_all_angles():
            self.op_set_all_target_angles_to_current_angles()
                        
            for motor_tag, motor in self.motors.items(): 
                if self.motors[motor_tag].angle_degrees > 180.0:
                    self.motors[motor_tag].apply_negative_angle_offset = True
                
        else:    
            print(f"[{self.tag}] error, unable to set all motor target angles, exiting thread!")
            return
       
                  
        while not self.exit_event.is_set():             
            start = time.time()        
            
            if self.is_error():
                print(f"[{self.tag}] error, exiting thread!")  
                self.cmd_all_motors_off()
                break           
                                   
            with self.comm_lock:
                
                #if self.motors_on == True:
                self._worker_set_all_targets()
                                
                self._worker_get_all_angles()  
                                       
                self._worker_get_all_status()
                
                self._worker_check_all_angle_limits()
                    
                #print(f"[Motors] processing time: {((time.time() - start) * 1000):0.2f}")                    
            
                                 
    ###############################################################################
    # General 
    ###############################################################################  
                    
    @staticmethod
    def is_angle_within_range(motor : Motor, tolerance: float) -> bool:        
        def normalize(angle):
            """Normalize the angle to be within the range of 0 to 360 degrees."""
            return angle % 360   
        difference = abs(normalize(motor.target_angle_degrees) - normalize(motor.angle_degrees))
        return difference <= tolerance or difference >= (360 - tolerance)
           
    def is_can_error(self):
        return self.can_interface.is_can_error()         
              
    def shutdown(self):
        if self.is_alive():
            self.exit_event.set()   
            self.join()    
        self.cmd_all_motors_off()
        self.can_interface.op_can_deinit()    
    
    ###############################################################################
    # Helpers
    ###############################################################################
 
    """ def angle_direction(self, motor_tag: str, current_angle : float, target_angle : float):   
        '''Determine the direction of movement from going from the current angle to the target angle'''
        difference = target_angle - current_angle
    
        # Normalize the difference to be within -180 to 180 degrees
        while difference > 180:
            difference -= 360
        while difference < -180:
            difference += 360
        
        direction = MotorDirection.COUNTER_CLOCKWISE if difference >= 0 else MotorDirection.CLOCKWISE        
        if motor_tag == 'FLH':
            print(f"[{self.tag}][{motor_tag}] current angle: {current_angle:0.2f}, target angle: {target_angle:0.2f}, difference: {difference:0.2f}, direction: {direction.name}")
        return direction """

###############################################################################
# Main / Entry - For Testing
###############################################################################
if __name__ == "__main__":
    
    print("Starting motor test...")

    try:   
        can_bus_id = 'can0'

        #motor_tags = ["FLA", "FLH", "FLK", "FRA", "FRH", "FRK"]     
        motor_tags = ["FLA", "FLH", "FLK"]
        
     
        motor_set_0 = Motors(can_bus_id=can_bus_id, motor_tags=motor_tags)        
              
        motor_set_0.cmd_all_motors_on()
        
        # Disabling prints from the can interface reduces time between transmissions.
        motor_set_0.can_interface.enable_prints(False)
         
       
        test = 1        
        if test == 0:    
            """
            Vibrate individual motors for identification and debugging.
            """             
            while(True):
                motor_set_0.op_motor_buzz(motor_tag="FLA", duration_seconds = 1)
                motor_set_0.op_motor_buzz(motor_tag="FLH", duration_seconds = 1)
                motor_set_0.op_motor_buzz(motor_tag="FLK", duration_seconds = 1)
        
        elif test ==  1:
            """
            Start the update thread, change target angles
            """
    
            motor_set_0.start()    
                
            while(True):
                motor_set_0.set_motor_targets(motor_tag="FLA", speed=2000, angle=90)   
                motor_set_0.set_motor_targets(motor_tag="FLH", speed=1500, angle=90)  
                motor_set_0.set_motor_targets(motor_tag="FLK", speed=1000, angle=90)           
                sleep(2)
                motor_set_0.set_motor_targets(motor_tag="FLA", speed=2000, angle=180)
                motor_set_0.set_motor_targets(motor_tag="FLH", speed=1500, angle=180)  
                motor_set_0.set_motor_targets(motor_tag="FLK", speed=1000, angle=180)  
                sleep(2)
                
        elif test ==  2:
            """
            Update the target angle and print current angle periodically
            """
            motor_set_0.start()   
            
            start_update = time.time()
            start_print = time.time()
            toggle = True
            while(True):
                if time.time() - start_update > 1: 
                    start_update = time.time() 
                    toggle = not toggle        
                    motor_set_0.set_motor_targets(motor_tag="FLA", speed=500, angle=45 if toggle else 270)                 
                if time.time() - start_print > 0.050: 
                    start_print = time.time()             
                    motors = motor_set_0.get_all_motors()  
                    print(motors["FLA"].angle_degrees)
      
    except Exception as e:
        print(e)
        print(traceback.format_exc())
    
    except KeyboardInterrupt:
        print ('Keyboard interrupt, exiting')
        
    finally:         
        motor_set_0.shutdown()       
                   
        sys.exit(0)   