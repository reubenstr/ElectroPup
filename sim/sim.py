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
#from MotionInputs import MotionInputs
      

commander = Commander()

np.set_printoptions(suppress=True)

model = mujoco.MjModel.from_xml_path('../model/scene.xml')
data = mujoco.MjData(model)

ctrl = np.array(model.keyframe("standing").ctrl)

with mujoco.viewer.launch_passive(model, data) as viewer:

  start = time.time()
  while viewer.is_running() and time.time() - start < 3000:
    step_start = time.time()

    # mj_step can be replaced with code that also evaluates
    # a policy and applies a control signal before stepping the physics.
   

    # Example modification of a viewer option: toggle contact points every two seconds.
    #with viewer.lock():
    #  viewer.opt.flags[mujoco.mjtVisFlag.mjVIS_CONTACTPOINT] = int(d.time % 2)


    commander.tick()
    joint_angles = commander.get_joint_angles()

 
    joint_names = [
        "front_left_abduction",   
        "front_left_hip",
        "front_left_knee"    
    ]

    #for jn in joint_names:
    #   print(jn, mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, jn) )


    #current_joint_positions = np.array([data.qpos[mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, jn)] for jn in joint_names])
    #print(current_joint_positions)

    """   target_positions = [angle, angle, angle]

    for idx, joint_name in enumerate(joint_names):
        joint_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, joint_name)
        data.ctrl[joint_id] = target_positions[idx] """

    """ # Manual pose test
    # FL
    joint_angles[0] = math.radians(0)
    joint_angles[1] = math.radians(-45)
    joint_angles[2] = math.radians(-90)
    #FR
    joint_angles[3] = math.radians(0)
    joint_angles[4] = math.radians(-45)
    joint_angles[5] = math.radians(-90)
    #BL
    joint_angles[6] = math.radians(0)
    joint_angles[7] = math.radians(-45)
    joint_angles[8] = math.radians(-90)
    #BR
    joint_angles[9] = math.radians(0)
    joint_angles[10] = math.radians(-45)
    joint_angles[11] = math.radians(-90) """

    ja = [math.degrees(radian) for radian in joint_angles]
    ja = [f"{num:.2f}" for num in ja]
    print(f"[JA] {ja[:]}")

    for i in range(12):
        data.ctrl[i] = joint_angles[i]


    commander.tick()


    mujoco.mj_step(model, data)
   
    viewer.sync()

    # Rudimentary time keeping, will drift relative to wall clock.
    #print(model.opt.timestep)
    time_until_next_step = model.opt.timestep - (time.time() - step_start)
    if time_until_next_step > 0:
      time.sleep(time_until_next_step)




commander.shutdown()