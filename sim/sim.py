#!/usr/bin/env python3

import os
import time
import yaml
import math
import mujoco
import mujoco.viewer
import numpy as np
import Gamepad

from Commander import Commander

# from MotionInputs import MotionInputs


commander = Commander()

np.set_printoptions(suppress=True)

model = mujoco.MjModel.from_xml_path("../model/scene.xml")
data = mujoco.MjData(model)

ctrl = np.array(model.keyframe("standing").ctrl)

with mujoco.viewer.launch_passive(model, data) as viewer:

    start = time.time()
    while viewer.is_running() and time.time() - start < 3000:
        step_start = time.time()

        # mj_step can be replaced with code that also evaluates
        # a policy and applies a control signal before stepping the physics.

        # Example modification of a viewer option: toggle contact points every two seconds.
        # with viewer.lock():
        #  viewer.opt.flags[mujoco.mjtVisFlag.mjVIS_CONTACTPOINT] = int(d.time % 2)

        commander.tick()
        joint_angles = commander.get_joint_angles()

        joint_names = [
            "front_left_abduction",
            "front_left_hip",
            "front_left_knee",
            "front_right_abduction",
            "front_right_hip",
            "front_right_knee",
            "back_left_abduction",
            "back_left_hip",
            "back_left_knee",
            "back_right_abduction",
            "back_right_hip",
            "back_right_knee",
        ]

        # Map joint angles from inverse kinematics to simulation model.

        target_positions = {}    
        target_positions['front_left_abduction'] = joint_angles['front_left'][0] * -1
        target_positions['front_left_hip'] = joint_angles['front_left'][1] + math.radians(-90)
        target_positions['front_left_knee'] = joint_angles['front_left'][2]
        target_positions['front_right_abduction'] = joint_angles['front_right'][0] * 1
        target_positions['front_right_hip'] = joint_angles['front_right'][1]  + math.radians(90)
        target_positions['front_right_knee'] = joint_angles['front_right'][2]
        target_positions['back_left_abduction'] = joint_angles['back_left'][0] * 1
        target_positions['back_left_hip'] = joint_angles['back_left'][1] + math.radians(-90)
        target_positions['back_left_knee'] = joint_angles['back_left'][2]
        target_positions['back_right_abduction'] = joint_angles['back_right'][0] * -1
        target_positions['back_right_hip'] = joint_angles['back_right'][1] + math.radians(90)
        target_positions['back_right_knee'] = joint_angles['back_right'][2]
   
        for _, (key, value) in enumerate(target_positions.items()):
            joint_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, key)
            data.ctrl[joint_id - 1] = target_positions[key] 

        """ j = np.zeros(12)

          j[0] = joint_angles[0]
          j[1] = joint_angles[1]
          j[2] = joint_angles[2]
          j[3] = joint_angles[6]
          j[4] = joint_angles[7]
          j[5] = joint_angles[8]
          j[6] = joint_angles[3]
          j[7] = joint_angles[4]
          j[8] = joint_angles[5]
          j[9] = joint_angles[9]
          j[10] = joint_angles[10]
          j[11] = joint_angles[11]

        ja = [math.degrees(radian) for radian in joint_angles]
        ja = [f"{num:.2f}" for num in ja]
        print(f"[JA] {ja[:]}")

        for i in range(12):
            data.ctrl[i] = joint_angles[i] """

        commander.tick()

        mujoco.mj_step(model, data)

        viewer.sync()

        # Rudimentary time keeping, will drift relative to wall clock.
        # print(model.opt.timestep)
        time_until_next_step = model.opt.timestep - (time.time() - step_start)
        if time_until_next_step > 0:
            time.sleep(time_until_next_step)


commander.shutdown()
