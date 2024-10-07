#!/usr/bin/python3

"""
    Controls a set of MG4010E-i10v3 actuators.
    
    Groups a collection of motors contained on a single CAN bus network.
    
    Class expects the hardware ID of the actuators to be 1 to number_of_motors

    Actuator driver limitations:
        - Does not auto select rotation direction to make shortest distance to target angle. 
            Therefore the library polls the motor angle and selects the rotation direction. 
        - The driver does not have a min and max angle, therefore there is a danger of collision.
        - CAN is no able to set torque limit, speed limit, etc. Only the UART interface is capable
            of setting these parameters.
             
            
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
           
        # Motor states:
        self.temperature : int = 0
        self.voltage : float = 0               
        self.watts : float = 0
        self.motor_speed : int = 0
        self.encoder_position : int = 0
        self.angle_degrees : float = 0
        
        # Motor fault states
        self.under_voltage_protection : bool = False
        self.over_voltage_protection  : bool = False
        self.over_temperature_protection : bool = False
        self.lost_input_protection : bool     = False    
        
        # Communication states:
        self.reply_timeout_count : int = 0


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
        
        self.tag = can_bus_id.upper()
        
        self.motors : Dict[str, Motor] = {} 
        for i, tag in enumerate(motor_tags):
            self.motors[tag] = Motor(tag=tag, motor_id = i + 1)
    
        self.can_interface = CanInterface(can_bus_id)
        self.can_interface.can_init()
        
        self.max_reply_timeouts_allow = 3
        
        self.halt = False
        
    ###############################################################################
    # Per Motor
    ###############################################################################      
 
    def motor_on(self, motor_tag : str):    
        start = time.time() 
        motor_id = self.motors[motor_tag].motor_id
        success = self.can_interface.cmd_motor_on(motor_id)  
        print(f"[{self.tag}][{motor_tag}] command on completed, success: {success}, time: {time.time() - start:0.3f}")   
        return success      
              
    def motor_off(self, motor_tag: str) :    
        start = time.time() 
        motor_id = self.motors[motor_tag].motor_id
        success = self.can_interface.cmd_motor_off(motor_id) 
        print(f"[{self.tag}][{motor_tag}] command off completed, success: {success}, time: {time.time() - start:0.3f}")   
        return success     
          
    def motor_set_zero_to_current_position(self, motor_tag: str):    
        start = time.time() 
        motor_id = self.motors[motor_tag].motor_id
        success = self.can_interface.cmd_set_zero_to_current_pos(motor_id)                
        print(f"[{self.tag}][{motor_tag}] command set zero to current position completed, success: {success}, time: {time.time() - start:0.3f}")    
        return success     
    
    def motor_buzz(self, motor_tag: str, duration_seconds : int):
        """Vibrates motors used to assist assembly and debugging"""
        motor_id = self.motors[motor_tag].motor_id
       
        print(f"[{self.tag}][{motor_tag}] buzzing motor {motor_tag} with ID {motor_id} for {duration_seconds} seconds")    

        start = time.time()
        
        while time.time() - start < duration_seconds:            
            self.can_interface.cmd_motor_increment_angle(motor_id, speed=250, angle=1)
            sleep(0.250)
            self.can_interface.cmd_motor_increment_angle(motor_id, speed=250, angle=-1)
            sleep(0.250)
               
            
    ###############################################################################
    # All Motors
    ###############################################################################      
               
    def motors_on(self):
        success = True
        start = time.time()
        for motor in self.motors.values():            
            success = self.can_interface.cmd_motor_on(motor.motor_id)
            if not success:
                success = False      
        print(f"[{self.tag}][ALL] command motors on completed, success: {success}, time: {time.time() - start:0.3f}")
        return success
                
    def motors_off(self):
        success = True
        start = time.time()
        for motor in self.motors.values():
            success = self.can_interface.cmd_motor_off(motor.motor_id)
            if not success:
                success = False       
        print(f"[{self.tag}][ALL] command motors off completed, success: {success}, time: {time.time() - start:0.3f}")
        return success
           
                
    ###############################################################################
    # Protected Getters and Setters
    ###############################################################################
       
    
    def set_motor_targets(self, motor_tag : str, speed : int, angle : float):         
        with self.lock:
            self.motors[motor_tag].target_speed = speed
            self.motors[motor_tag].target_angle_degrees = angle
    
    def get_motor_targets(self,  motor_tag : str):      
        with self.lock:                    
            return self.motors[motor_tag].target_speed, self.motors[motor_tag].target_angle_degrees
        
    def get_motors(self):      
        with self.lock:                    
            return self.motors.copy()
        
    def get_motor_angle(self, motor_tag : str):      
        with self.lock:                    
            return self.motors[motor_tag].angle_degrees
        
    def op_set_target_angle_to_current_angle(self):
        """
        Sets all motor target angles to current current
        
        :return: True if all angles have been set, False if a motor did not reply to the command        
        """
        for motor_tag, motor in self.motors.items():                      
            sensor_angle = self.can_interface.req_motor_single_angle(motor.motor_id)  
            if sensor_angle:
                self.motors[motor_tag].target_angle_degrees = sensor_angle                
            else:
                return False 
        return True                            
                
        
    ###############################################################################
    # Worker
    ###############################################################################
        
    def _worker_set_all_targets(self):
        """Send target speed and angle to the motors"""
        for motor_tag, motor in self.motors.items():   
            speed, angle = self.get_motor_targets (motor_tag)                                      
            
            sensor_angle = self.can_interface.req_motor_single_angle(motor.motor_id)  
            if sensor_angle:
                self.motors[motor_tag].angle_degrees = sensor_angle
                self.motors[motor_tag].reply_timeout_count = 0 
            else:
                self.motors[motor_tag].reply_timeout_count += 1   
                continue                               
                         
            direction = self.angle_direction(motor_tag = motor_tag, current_angle=sensor_angle, target_angle=angle)    
            success = self.can_interface.cmd_motor_single_angle(motor.motor_id, direction.value, speed, angle)  
            if success:
                self.motors[motor_tag].reply_timeout_count = 0 
            else:
                self.motors[motor_tag].reply_timeout_count += 1   
                           
    
    def _worker_get_all_status(self):
        """Get motor status from the motors"""        
        for motor_tag, motor in self.motors.items():   
            result = self.can_interface.req_state_1(motor.motor_id)  
            if result:
                self.motors[motor_tag].reply_timeout_count = 0 
            else:
                self.motors[motor_tag].reply_timeout_count += 1   
                continue
            
            with self.lock:             
                self.motors[motor_tag].temperature = result['temperature']
                self.motors[motor_tag].voltage = result['voltage']
                self.motors[motor_tag].under_voltage_protection = result['under_voltage_protection']  
                self.motors[motor_tag].over_voltage_protection = result['over_voltage_protection']
                self.motors[motor_tag].over_temperature_protection = result['over_temperature_protection']
                self.motors[motor_tag].lost_input_protection = result['lost_input_protection']  

    def _worker_check_for_errors(self):
        """Check motor status for errors"""        
        with self.lock: 
            if self.is_error(self.motors):
                self.halt = True
                print(f"[{self.tag}] *** HALT STATE ***")                
                self.motors_off()
       
    def run(self):      
        """
        Main function that continously updates motor targets (speed, position) and checks for errors.
        """  
                
        if self.halt:
            print(f"[{self.tag}] error, unable to start thread, in a halt state!")
            return
        else:
            print(f"[{self.tag}] thread started")
            
        if self.op_set_target_angle_to_current_angle():    
            print(f"[{self.tag}] target angles set to current angles")
        else:
            print(f"[{self.tag}] error, unable to set all motor target angles, exiting thread!")
            return

        while not self.exit_event.is_set() and not self.halt: 
            
            #start = time.time()          
                        
            self._worker_set_all_targets()
            
            #self._worker_get_all_status()
            
            self._worker_check_for_errors()  
            
            #print(f"{((time.time() - start) * 1000):0.2f}")
            
            sleep(0.010)
                    
        
        
    ###############################################################################
    # General 
    ###############################################################################  
    
    
    def is_error(self, motors : Dict[str, Motor]) :
        """        
        Args:
            motors (Dict[str, Motor]): _description_

        Returns:
            bool: True if motor contains a fault state or comms error
        """
        error = False
        for motor_tag, motor in motors.items():
            if motor.under_voltage_protection or motor.over_voltage_protection or motor.over_temperature_protection or motor.lost_input_protection:                 
                error = True
            if motor.reply_timeout_count > self.max_reply_timeouts_allow:
               error = True
        return error
        
                        
    def is_halted(self):
        return self.halt
       
    def shutdown(self):
        self.exit_event.set()   
        self.join()    
        self.motors_off()
        self.can_interface.can_deinit()    
                       
    
    ###############################################################################
    # Helpers
    ###############################################################################
 
    def angle_direction(self, motor_tag: str, current_angle : float, target_angle : float):   
        """Determine the direction of movement from going from the current angle to the target angle"""
        difference = target_angle - current_angle
    
        # Normalize the difference to be within -180 to 180 degrees
        while difference > 180:
            difference -= 360
        while difference < -180:
            difference += 360
        
        direction = MotorDirection.COUNTER_CLOCKWISE if difference >= 0 else MotorDirection.CLOCKWISE        
        if motor_tag == 'FLH':
            print(f"[{self.tag}][{motor_tag}] current angle: {current_angle:0.2f}, target angle: {target_angle:0.2f}, difference: {difference:0.2f}, direction: {direction.name}")
        return direction


###############################################################################
# Main / Entry - For Testing
###############################################################################
if __name__ == "__main__":
    
    print("Starting MotorSet test...")

    try:   
        can_bus_id = 'can0'

        #motor_tags = ["FLA", "FLH", "FLK", "FRA", "FRH", "FRK"]     
        motor_tags = ["FLA", "FLH", "FLK"]
        
     
        motor_set_0 = Motors(can_bus_id=can_bus_id, motor_tags=motor_tags)        
              
        motor_set_0.motors_on()
        
        # Disabling prints from the can interface reduces time between transmissions.
        motor_set_0.can_interface.enable_prints(False)
         
       
        test = 1        
        if test == 0:    
            """
            Vibrate individual motors for identification and debugging.
            """             
            while(True):
                motor_set_0.motor_buzz(motor_tag="FLA", duration_seconds = 1)
                motor_set_0.motor_buzz(motor_tag="FLH", duration_seconds = 1)
                motor_set_0.motor_buzz(motor_tag="FLK", duration_seconds = 1)
        
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
                    motors = motor_set_0.get_motors()  
                    print(motors["FLA"].angle_degrees)
                  
             
    
    except Exception as e:
        print(e)
        print(traceback.format_exc())
    
    except KeyboardInterrupt:
        print ('Keyboard interrupt, exiting')
        
    finally:         
        motor_set_0.shutdown()       
                   
        sys.exit(0)
   