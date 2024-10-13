#!/usr/bin/env python3

"""
   
"""
import traceback
from math import pi
from time import sleep
from rich import print # Overrides print and injects colors

# Local source.
from quadruped.body import Body
from quadruped.gamepad_interface import GamepadInterface
from quadruped.parameters.frame_parameters import FrameParameters
from quadruped.parameters.motion_parameters import MotionParameters
from motors.motors import Motors


###############################################################################
# Entry
###############################################################################
if __name__ == "__main__":

    motion_parameters_filepath = "./quadruped/parameters/motion_parameters.yaml"
    frame_parameters_filepath = "./quadruped/parameters/frame_parameters.yaml"

    frame_parameters = FrameParameters(frame_parameters_filepath)
    motion_parameters = MotionParameters(motion_parameters_filepath)

    gamepad_interface = GamepadInterface(motion_parameters)
    gamepad_connected = gamepad_interface.connect_gamepad()
    
    body = Body(frame_parameters=frame_parameters)


    motor_tags = ["FLA", "FLH", "FLK", "FRA", "FRH", "FRK"]     
    #motor_tags = ["FLA", "FLH", "FLK"]
    motor_interface_front = Motors(can_bus_id="can0", motor_tags=motor_tags)
 
    
    #motor_tags_back = ["BLA", "BLH", "BLK", "BRA", "BRH", "BRK"]
    # motor_interface_back = Motors(can_bus_id="can1", motor_tags=motor_tags_back)  
    #motor_interface_back.cmd_all_motors_off()
    
      
    motor_interface_front.cmd_all_motors_on()
    
    motor_interface_front.start()
    
    
    

    try:
        while gamepad_interface.is_connected():

            if gamepad_connected:
                motion_parameters = gamepad_interface.get_motion_parameters()
                
                error_state = body.set_body_pose_by_transform_inputs(
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
                    joint_angles = body.get_joint_angles()

                    #motors_front.set_motor_targets(motor_tag="FLA", speed=500, angle=joint_angles['front_left']['abduction'])   
                    #motors_front.set_motor_targets(motor_tag="FLH", speed=500, angle=joint_angles['front_left']['hip'])  
                    #motors_front.set_motor_targets(motor_tag="FLK", speed=500, angle=joint_angles['front_left']['knee']) 
                    
                    fla=joint_angles['front_left']['abduction']  
                    flh=joint_angles['front_left']['hip']  
                    flk=joint_angles['front_left']['knee']  
                    
              
                         
                    
                    speed = 2500
                    motor_interface_front.set_motor_targets(motor_tag="FLA", speed=speed, angle=fla)   
                    motor_interface_front.set_motor_targets(motor_tag="FLH", speed=speed, angle=flh)  
                    motor_interface_front.set_motor_targets(motor_tag="FLK", speed=speed, angle=flk) 
                    
                    if not motor_interface_front.is_alive():
                        motors = motor_interface_front.get_all_motors()
                        for motor_tag, motor in motors.items():
                            print(f"[{motor_tag}] {motor.reply_timeout_count}")
                            
                            # is_can_error
                            
                    
               

            sleep(0.010)
            
    except KeyboardInterrupt:
        print ('Keyboard interrupt, exiting')
        
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
        
    finally:          
        motor_interface_front.shutdown()
        gamepad_interface.disconnect()
