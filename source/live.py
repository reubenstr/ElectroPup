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

    #motor_tags = ["FLA", "FLH", "FLK", "FRA", "FRH", "FRK"]     
    motor_tags = ["FLA", "FLH", "FLK"]
    motors_front = Motors(can_bus_id="can0", motor_tags=motor_tags)
    
    motors_front.motors_on()
    
    motors_front.start()

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
                
                if error_state == Body.ErrorState.NONE:
                    joint_angles = body.get_joint_angles()

                    #motors_front.set_motor_targets(motor_tag="FLA", speed=500, angle=joint_angles['front_left']['abduction'])   
                    #motors_front.set_motor_targets(motor_tag="FLH", speed=500, angle=joint_angles['front_left']['hip'])  
                    #motors_front.set_motor_targets(motor_tag="FLK", speed=500, angle=joint_angles['front_left']['knee']) 
                    
                    fla=joint_angles['front_left']['abduction']  
                    flh=joint_angles['front_left']['hip']  
                    flk=joint_angles['front_left']['knee']  
                    
                    #fla = 0
                    
                    a1 = motors_front.get_motor_angle("FLA")
                    a2 = motors_front.get_motor_angle("FLH")
                    a3 = motors_front.get_motor_angle("FLK")
                    
                    print(f"{fla:0.2f}, {a1:0.2f} | {flh:0.2f}, {a2:0.2f} | {flk:0.2f}, {a3:0.2f}")
                    
                    
                    motors_front.set_motor_targets(motor_tag="FLA", speed=1000, angle=fla)   
                    motors_front.set_motor_targets(motor_tag="FLH", speed=1000, angle=flh)  
                    motors_front.set_motor_targets(motor_tag="FLK", speed=1000, angle=flk) 
                    
                else:
                    print(error_state.name)
                    pass

            sleep(0.010)
            
    except KeyboardInterrupt:
        print ('Keyboard interrupt, exiting')
        
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
        
    finally:          
        motors_front.shutdown()
        gamepad_interface.disconnect()
