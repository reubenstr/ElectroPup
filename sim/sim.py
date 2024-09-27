#!/usr/bin/env python3

import os
import time
import math
import traceback
import mujoco
import mujoco.viewer
import numpy as np

from quadruped.body import Body
from quadruped.gamepad_interface import GamepadInterface
from quadruped.parameters.frame_parameters import FrameParameters
from quadruped.parameters.motion_parameters import MotionParameters

# np.set_printoptions(suppress=True)

class Simulation():

    def __init__(self):
        self.model = mujoco.MjModel.from_xml_path("./model/scene.xml")

        self.data = mujoco.MjData(self.model)

        keyframe = np.array(self.model.keyframe("standing").ctrl)

        self.viewer = mujoco.viewer.launch_passive(self.model, self.data)
        
        # https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjtvisflag
        self.viewer.opt.flags[mujoco.mjtVisFlag.mjVIS_CONTACTPOINT] =  True
        self.viewer.opt.flags[mujoco.mjtVisFlag.mjVIS_COM] =  False
        self.viewer.opt.flags[mujoco.mjtVisFlag.mjVIS_CONTACTFORCE] =  False
          
    def is_running(self):
        return self.viewer.is_running()
    
    def get_timestep(self):
        return self.model.opt.timestep


    def tick(self, joint_angles):
                  
        # Map joint angles from inverse kinematics to joint names of simulation model.
        target_positions = {}    
        target_positions['front_left_abduction'] = joint_angles['front_left'][0] * -1
        target_positions['front_left_hip'] = joint_angles['front_left'][1] 
        target_positions['front_left_knee'] = joint_angles['front_left'][2]
        target_positions['front_right_abduction'] = joint_angles['front_right'][0] * 1
        target_positions['front_right_hip'] = joint_angles['front_right'][1] 
        target_positions['front_right_knee'] = joint_angles['front_right'][2]
        target_positions['back_left_abduction'] = joint_angles['back_left'][0] * 1
        target_positions['back_left_hip'] = joint_angles['back_left'][1]
        target_positions['back_left_knee'] = joint_angles['back_left'][2]
        target_positions['back_right_abduction'] = joint_angles['back_right'][0] * -1
        target_positions['back_right_hip'] = joint_angles['back_right'][1] 
        target_positions['back_right_knee'] = joint_angles['back_right'][2]

        #for key in target_positions.keys():
        #    target_positions[key] = 0
   
        # Apply target positions to simulation model.
        for _, (key, value) in enumerate(target_positions.items()):
            joint_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_JOINT, key)
            self.data.ctrl[joint_id - 1] = target_positions[key] 

        mujoco.mj_step(self.model, self.data)

        self.viewer.sync()

###############################################################################
# Entry
###############################################################################
if __name__ == "__main__":

    simulation = Simulation()

    frame_parameters = FrameParameters("./quadruped/parameters/frame_parameters.yaml")
    motion_parameters = MotionParameters("./quadruped/parameters/motion_parameters.yaml")

    gamepad_interface = GamepadInterface(motion_parameters)
    gamepad_connected = gamepad_interface.connect_gamepad()

    body = Body(frame_parameters=frame_parameters)
   
    start = time.time()
    
    try:

        # TODO: check for gamepad disconnect
        while True: #simulation.is_running():
            step_start = time.time() 
            
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

                simulation.tick(joint_angles)

            # Delay between simulation steps.
            time_until_next_step = simulation.get_timestep() - (time.time() - step_start)
            if time_until_next_step > 0:
                time.sleep(time_until_next_step)
    
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())

    finally:
        gamepad_interface.disconnect()    


    

   
