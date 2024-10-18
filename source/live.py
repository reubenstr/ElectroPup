#!/usr/bin/env python3

"""
   
"""
import traceback
from math import pi
from time import sleep
from rich import print # Overrides print and injects colors
from math import degrees

# Local source.
from quadruped.body import Body
from quadruped.gamepad_interface import GamepadInterface
from quadruped.parameters.frame_parameters import FrameParameters
from quadruped.parameters.motion_parameters import MotionParameters, KineticState, ControllerEvent
from motors.motors import Motors


class Live():
    def __init__(self):
        motion_parameters_filepath = "./quadruped/parameters/motion_parameters.yaml"
        frame_parameters_filepath = "./quadruped/parameters/frame_parameters.yaml"

        frame_parameters = FrameParameters(frame_parameters_filepath)
        motion_parameters = MotionParameters(motion_parameters_filepath)

        self.gamepad_interface = GamepadInterface(motion_parameters)
        self.gamepad_interface.register_controller_event_callback(self.controller_event_callback)
        self.gamepad_interface.connect_gamepad()
        
        
        self.body = Body(frame_parameters=frame_parameters)

        #motor_tags = ["FLA", "FLH", "FLK", "FRA", "FRH", "FRK"]     
        motor_tags = ["FLA", "FLH", "FLK"]
        self.motor_interface_front = Motors(can_bus_id="can0", motor_tags=motor_tags)
        self.motor_interface_front.cmd_all_motors_off()
        
        
        self.motor_interface_front.set_limits("FLA", degrees(frame_parameters.abduction_joint_lower_bounds), degrees(frame_parameters.abduction_joint_upper_bounds))
        self.motor_interface_front.set_limits("FLH", degrees(frame_parameters.hip_joint_lower_bounds), degrees(frame_parameters.hip_joint_upper_bounds))
        self.motor_interface_front.set_limits("FLK", degrees(frame_parameters.knee_joint_lower_bounds), degrees(frame_parameters.knee_joint_upper_bounds))

         
        
                
        #motor_tags_back = ["BLA", "BLH", "BLK", "BRA", "BRH", "BRK"]
        # motor_interface_back = Motors(can_bus_id="can1", motor_tags=motor_tags_back)  
        #motor_interface_back.cmd_all_motors_off()
          
                
        self.kinetic_state : KineticState = KineticState.STARTUP
        self.previous_kinetic_state : KineticState = KineticState.INIT        
        self.speed : int = 0
        
        
    def controller_event_callback(self, event : ControllerEvent):    
        print(f"[EVENT] controller event received: {event.name}")
        if event == ControllerEvent.KINETIC_STATE_TOGGLE:        
            if self.kinetic_state == KineticState.POSE:
                self.kinetic_state = KineticState.MOTION
            elif self.kinetic_state == KineticState.MOTION:
                self.kinetic_state = KineticState.POSE 
        elif event == ControllerEvent.MOTOR_POWER_TOGGLE: 
            if self.kinetic_state == KineticState.HALT: 
                self.kinetic_state = KineticState.STAND 
            elif self.kinetic_state != KineticState.ERROR: 
                self.kinetic_state = KineticState.HALT                    

                    
    def apply_controller_input(self):                
        motion_parameters = self.gamepad_interface.get_motion_parameters()
        
        error_state = self.body.set_body_pose_by_transform_inputs(
            phi=motion_parameters.roll,
            theta=motion_parameters.pitch,
            psi=motion_parameters.yaw,
            x=motion_parameters.side_translation,
            y=motion_parameters.height_translation,
            z=motion_parameters.forward_translation,
        )
        if error_state == Body.ErrorState.IK or error_state == Body.ErrorState.JOINT:
            print(error_state.name)
        elif error_state == Body.ErrorState.NONE:
            joint_angles = self.body.get_joint_angles()

            #motors_front.set_motor_targets(motor_tag="FLA", speed=500, angle=joint_angles['front_left']['abduction'])   
            #motors_front.set_motor_targets(motor_tag="FLH", speed=500, angle=joint_angles['front_left']['hip'])  
            #motors_front.set_motor_targets(motor_tag="FLK", speed=500, angle=joint_angles['front_left']['knee']) 
            
            fla=joint_angles['front_left']['abduction']  
            flh=joint_angles['front_left']['hip']  
            flk=joint_angles['front_left']['knee']  
                            
            self.motor_interface_front.set_motor_targets(motor_tag="FLA", speed=self.speed, angle=fla)   
            self.motor_interface_front.set_motor_targets(motor_tag="FLH", speed=self.speed, angle=flh)  
            self.motor_interface_front.set_motor_targets(motor_tag="FLK", speed=self.speed, angle=flk) 
            
            """ if not self.motor_interface_front.is_alive():
                motors = self.motor_interface_front.get_all_motors()
                for motor_tag, motor in motors.items():
                    print(f"[{motor_tag}] {motor.reply_timeout_count}")
                    
                    # is_can_error """
                    
    def temp_standing_pose(self):    
        """
            TEMP TO TEST STANDING POST PRIOR TO PLACEMENT
        """                
        motion_parameters = MotionParameters("./quadruped/parameters/motion_parameters.yaml")
        
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
            joint_angles = self.body.get_joint_angles()

            
            fla=joint_angles['front_left']['abduction']  
            flh=joint_angles['front_left']['hip']  
            flk=joint_angles['front_left']['knee']                              
            self.motor_interface_front.set_motor_targets(motor_tag="FLA", speed=self.speed, angle=fla)   
            self.motor_interface_front.set_motor_targets(motor_tag="FLH", speed=self.speed, angle=flh)  
            self.motor_interface_front.set_motor_targets(motor_tag="FLK", speed=self.speed, angle=flk) 
                     
                
    ###############################################################################
    # Main Loop
    ###############################################################################       
        
    def run(self):
        while True:
        
            if not self.gamepad_interface.is_connected():  
                return
            
            self.gamepad_interface.tick(self.kinetic_state)
            
            # Execute once after kinetic state change:            
            if self.previous_kinetic_state != self.kinetic_state:   
                self.previous_kinetic_state = self.kinetic_state
                print(f"[STATE] kinetic state changed to: {self.kinetic_state.name}")
                             
                if self.kinetic_state == KineticState.ERROR:
                    self.motor_interface_front.cmd_all_motors_off()
                    #self.motor_interface_back.cmd_all_motors_off()    
                
                elif self.kinetic_state == KineticState.STARTUP:
                    self.motor_interface_front.start()
                    #self.motor_interface_back.start()
                    self.kinetic_state = KineticState.HALT
                
                elif self.kinetic_state == KineticState.HALT:
                    self.motor_interface_front.cmd_all_motors_off()
                    #self.motor_interface_back.cmd_all_motors_off()
                
                elif self.kinetic_state == KineticState.STAND: 
                    self.speed = 500                
                    self.temp_standing_pose()                      
                    self.motor_interface_front.cmd_all_motors_on()
                    #self.motor_interface_back.cmd_all_motors_on()                                    
                    
                                
                elif self.kinetic_state == KineticState.POSE:
                    self.speed = 2500                      
                elif self.kinetic_state == KineticState.MOTION:
                    self.speed = 2500
                      
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
                self.apply_controller_input()  
            elif self.kinetic_state == KineticState.MOTION:               
                #self.apply_controller_input()   
                pass
            elif self.kinetic_state == KineticState.FLIP:
                pass
                   
           
            if self.motor_interface_front.is_error(): # and self.motor_interface_back.is_error() == False 
                self.kinetic_state = KineticState.ERROR
            
           
            
            #sleep(0.200)      
            sleep(0.010)
    
    ###############################################################################
    # Helpers
    ###############################################################################   
                 
    def shutdown(self):
        self.motor_interface_front.shutdown()
        self.gamepad_interface.disconnect()

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
