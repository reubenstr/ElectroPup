#!/usr/bin/env python3

import os
import time
import yaml
import mujoco
import mujoco.viewer
import numpy as np


import quad_commander


from joystick_interpreter import JoystickInterpreter
from motion_inputs import MotionInputs


motion_parameters_filepath = "./parameters/motion_parameters.yaml"
if os.path.exists(motion_parameters_filepath):
    with open(motion_parameters_filepath, 'r') as stream:
        motion_parameters = yaml.safe_load(stream)
else:
    print(f"[SYSTEM] parameter file not found! {motion_parameters_filepath}")
    exit(1)

joystick_interpreter = JoystickInterpreter(motion_parameters)
motion_inputs = MotionInputs()

   
      

system = quad_commander.System()

np.set_printoptions(suppress=True)

model = mujoco.MjModel.from_xml_path('../model/scene.xml')
data = mujoco.MjData(model)


angle = 0

ctrl= np.array(model.keyframe("standing").ctrl)

with mujoco.viewer.launch_passive(model, data) as viewer:


  start = time.time()
  while viewer.is_running() and time.time() - start < 30:
    step_start = time.time()

    # mj_step can be replaced with code that also evaluates
    # a policy and applies a control signal before stepping the physics.
   

    # Example modification of a viewer option: toggle contact points every two seconds.
    #with viewer.lock():
    #  viewer.opt.flags[mujoco.mjtVisFlag.mjVIS_CONTACTPOINT] = int(d.time % 2)

 
    joint_names = [
        "front_left_abduction",   
        "front_left_hip",
        "front_left_knee"    
    ]

    for jn in joint_names:
       print(jn, mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, jn) )


    current_joint_positions = np.array([data.qpos[mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, jn)] for jn in joint_names])
    print(current_joint_positions)

    target_positions = [angle, angle, angle]

    for idx, joint_name in enumerate(joint_names):
        joint_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, joint_name)
        data.ctrl[joint_id] = target_positions[idx]

    for i in range(12):
        data.ctrl[i] = ctrl[i]

    motion_inputs = joystick_interpreter.get_motion_inputs(axes, buttons)

    system.tick()


    mujoco.mj_step(model, data)

    angle += 0.001

    # Pick up changes to the physics state, apply perturbations, update options from GUI.
    viewer.sync()

    # Rudimentary time keeping, will drift relative to wall clock.
    print(model.opt.timestep)
    time_until_next_step = model.opt.timestep - (time.time() - step_start)
    if time_until_next_step > 0:
      time.sleep(time_until_next_step)


