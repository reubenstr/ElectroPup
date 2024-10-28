#!/usr/bin/env python3

"""

    
   
"""

import time
import traceback
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


class Live():
    def __init__(self):
        motion_parameters_filepath = "./system/parameters/motion_parameters.yaml"
        frame_parameters_filepath = "./system/parameters/frame_parameters.yaml"

        frame_parameters = FrameParameters(frame_parameters_filepath)
        self.motion_parameters = MotionParameters(motion_parameters_filepath)

        self.gamepad = Gamepad(self.motion_parameters)
        self.gamepad.register_controller_event_callback(self.controller_event_callback)
           
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
          
                
        self.aux = Aux()        
                
        self.kinetic_state : KineticState = KineticState.STARTUP
        self.previous_kinetic_state : KineticState = KineticState.INIT  
        self.body_error_state : Body.ErrorState = Body.ErrorState.NONE      
        self.speed : int = 0
        
        self.loop_time : float = 0
        
        
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

                    
                    
                    
                    
    def apply_controller_input(self, motion_parameters : MotionParameters):                
              
        self.body_error_state = self.body.set_body_pose_by_transform_inputs(
            phi=motion_parameters.roll,
            theta=motion_parameters.pitch,
            psi=motion_parameters.yaw,
            x=motion_parameters.side_translation,
            y=motion_parameters.height_translation,
            z=motion_parameters.forward_translation,
        )
        
        if self.body_error_state == Body.ErrorState.IK or self.body_error_state == Body.ErrorState.JOINT:
            print(f"[Body] error, {self.body_error_state.name}")
            return
              
        joint_angles = self.body.get_joint_angles(units="DEGREES") 
        self.motor_interface_front.set_motor_targets(motor_tag="FLA", speed=self.speed, angle=joint_angles['front_left']['abduction'])   
        self.motor_interface_front.set_motor_targets(motor_tag="FLH", speed=self.speed, angle=joint_angles['front_left']['hip'])  
        self.motor_interface_front.set_motor_targets(motor_tag="FLK", speed=self.speed, angle=joint_angles['front_left']['knee']) 
        self.motor_interface_front.set_motor_targets(motor_tag="FRA", speed=self.speed, angle=-joint_angles['front_right']['abduction'])   
        self.motor_interface_front.set_motor_targets(motor_tag="FRH", speed=self.speed, angle=joint_angles['front_right']['hip'])  
        self.motor_interface_front.set_motor_targets(motor_tag="FRK", speed=self.speed, angle=joint_angles['front_right']['knee']) 
        self.motor_interface_back.set_motor_targets(motor_tag="BLA", speed=self.speed, angle=joint_angles['back_right']['abduction'])   
        self.motor_interface_back.set_motor_targets(motor_tag="BLH", speed=self.speed, angle=joint_angles['back_left']['hip'])  
        self.motor_interface_back.set_motor_targets(motor_tag="BLK", speed=self.speed, angle=joint_angles['back_left']['knee']) 
        self.motor_interface_back.set_motor_targets(motor_tag="BRA", speed=self.speed, angle=-joint_angles['back_left']['abduction'])   
        self.motor_interface_back.set_motor_targets(motor_tag="BRH", speed=self.speed, angle=joint_angles['back_right']['hip'])  
        self.motor_interface_back.set_motor_targets(motor_tag="BRK", speed=self.speed, angle=joint_angles['back_right']['knee']) 
            
     
                    
    def temp_standing_pose(self):    
        """
            TEMP TO TEST STANDING POST PRIOR TO PLACEMENT
        """                
        motion_parameters = MotionParameters("./system/parameters/motion_parameters.yaml")
        
        error_state = self.body.set_body_pose_by_transform_inputs(
            phi=0,
            theta=0,
            psi=0,
            x=0,
            y=(motion_parameters.height_translation_min + motion_parameters.height_translation_max)/2,
            z=0,
        )
        if error_state == Body.ErrorState.IK or error_state == Body.ErrorState.JOINT:
            print(error_state.name)
        elif error_state == Body.ErrorState.NONE:
            joint_angles = self.body.get_joint_angles("DEGREES")
            
            fla=joint_angles['front_left']['abduction']  
            flh=joint_angles['front_left']['hip']  
            flk=joint_angles['front_left']['knee'] 
            fra=joint_angles['front_right']['abduction']  
            frh=joint_angles['front_right']['hip']  
            frk=joint_angles['front_right']['knee']     
            bla=joint_angles['back_right']['abduction']  
            blh=joint_angles['back_left']['hip']  
            blk=joint_angles['back_left']['knee'] 
            bra=joint_angles['back_left']['abduction']  
            brh=joint_angles['back_right']['hip']  
            brk=joint_angles['back_right']['knee']                              
            self.motor_interface_front.set_motor_targets(motor_tag="FLA", speed=self.speed, angle=fla)   
            self.motor_interface_front.set_motor_targets(motor_tag="FLH", speed=self.speed, angle=flh)  
            self.motor_interface_front.set_motor_targets(motor_tag="FLK", speed=self.speed, angle=flk) 
            self.motor_interface_front.set_motor_targets(motor_tag="FRA", speed=self.speed, angle=fra)   
            self.motor_interface_front.set_motor_targets(motor_tag="FRH", speed=self.speed, angle=frh)  
            self.motor_interface_front.set_motor_targets(motor_tag="FRK", speed=self.speed, angle=frk) 
            self.motor_interface_back.set_motor_targets(motor_tag="BLA", speed=self.speed, angle=bla)   
            self.motor_interface_back.set_motor_targets(motor_tag="BLH", speed=self.speed, angle=blh)  
            self.motor_interface_back.set_motor_targets(motor_tag="BLK", speed=self.speed, angle=blk) 
            self.motor_interface_back.set_motor_targets(motor_tag="BRA", speed=self.speed, angle=bra)   
            self.motor_interface_back.set_motor_targets(motor_tag="BRH", speed=self.speed, angle=brh)  
            self.motor_interface_back.set_motor_targets(motor_tag="BRK", speed=self.speed, angle=brk) 
                     
                
    ###############################################################################
    # Main Loop
    ###############################################################################       
        
    def run(self):
        while True:
        
            if not self.gamepad.is_connected():  
                sleep(0.100)
                continue
                      
            self.gamepad.set_kinetic_state(self.kinetic_state)    
                        
            # Execute once after kinetic state change:                      
            if self.previous_kinetic_state != self.kinetic_state:   
                self.previous_kinetic_state = self.kinetic_state
                print(f"[STATE] kinetic state changed to: {self.kinetic_state.name}")
                             
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
                    self.apply_controller_input(self.motion_parameters)                      
                    self.motor_interface_front.cmd_all_motors_on()
                    self.motor_interface_back.cmd_all_motors_on()                                    
                                                    
                elif self.kinetic_state == KineticState.POSE:
                    self.speed = 2000                       
                elif self.kinetic_state == KineticState.MOTION:
                    self.speed = 1000
                      
                elif self.kinetic_state == KineticState.FLIP:
                    pass
                                
            
            # Kinetic state machine:        
            if self.kinetic_state == KineticState.ERROR:
                pass
           
            elif self.kinetic_state == KineticState.HALT:
                pass
            
            elif self.kinetic_state == KineticState.STAND:                       
                if self.motor_interface_front.op_is_all_motor_angles_within_range(0.5):
                    self.kinetic_state = KineticState.POSE
            
            elif self.kinetic_state == KineticState.POSE:    
                motion_parameters = self.gamepad.get_motion_parameters()            
                self.apply_controller_input(motion_parameters)  
            
            elif self.kinetic_state == KineticState.MOTION:               
                motion_parameters = self.gamepad.get_motion_parameters()            
                self.apply_controller_input(motion_parameters)              
           
            elif self.kinetic_state == KineticState.FLIP:
                pass

           
            self.process_aux()
            
            if self.motor_interface_front.is_error() or self.motor_interface_back.is_error(): 
                self.kinetic_state = KineticState.ERROR
              
            self.sleep_loop()
       
       
   
       
    ###############################################################################
    # Auxiliary
    ###############################################################################        
    
    def process_aux(self):
        message = StatusMessage()  
        
        self.joint_angle_error  = False
        self.inverse_kinematics_error = False
        message.joystick_error = self.gamepad.is_connected() == False
        message.can_error = self.motor_interface_front.is_can_error() or self.motor_interface_back.is_can_error()
        
        voltage_accumulator : float = 0.0
        motors : Dict[str, Motor] = self.motor_interface_front.get_all_motors() | self.motor_interface_back.get_all_motors()
        for index, (motor_tag, motor) in enumerate(motors.items()):
            message.motor_ons[index] = motor.is_on()
            message.motor_errors[index] = motor.is_error()  
            if motor.under_voltage_protection == True:
                message.under_voltage_error = True
            if motor.over_temperature_protection == True:
                message.over_temperature_error = True
            voltage_accumulator += motor.voltage
                                                   
        message.battery_voltage = voltage_accumulator / len(motors)
                 
        self.aux.send_at_rate(message.pack(), 1) 
        
            
    ###############################################################################
    # Helpers
    ###############################################################################   
    
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
                 
    def shutdown(self):
        self.motor_interface_front.shutdown()
        self.gamepad.disconnect()

###############################################################################
# Entry
###############################################################################
if __name__ == "__main__":

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
