import time
import traceback
import mujoco
import mujoco.viewer
import numpy as np
from math import radians

from quadruped.quad import Quad, AngleUnits, LegName
from quadruped.parameters import ik_parameters, motion_parameters
from input.input import Input

"""
    Shows the quadruped in Mujoco simulation enviroment.

    Only pose is implemented.

    TODO:
        Apply the motion controller for walking, etc.
"""

# np.set_printoptions(suppress=True)


class Simulation:

    def __init__(self):
        self.model = mujoco.MjModel.from_xml_path("./model/scene.xml")

        self.data = mujoco.MjData(self.model)

        keyframe = np.array(self.model.keyframe("standing").ctrl)

        self.viewer = mujoco.viewer.launch_passive(self.model, self.data)

        # https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjtvisflag
        self.viewer.opt.flags[mujoco.mjtVisFlag.mjVIS_CONTACTPOINT] = False
        self.viewer.opt.flags[mujoco.mjtVisFlag.mjVIS_COM] = False
        self.viewer.opt.flags[mujoco.mjtVisFlag.mjVIS_CONTACTFORCE] = False

    def is_running(self):
        return self.viewer.is_running()

    def get_timestep(self):
        return self.model.opt.timestep

    def tick(self, joint_angles):

        # Map joint angles from inverse kinematics to joint names of simulation model.
        target_positions = {}
        target_positions["front_left_abduction"] = joint_angles[LegName.FL]["abduction"]
        target_positions["front_left_hip"] = joint_angles[LegName.FL]["hip"]
        target_positions["front_left_knee"] = joint_angles[LegName.FL]["knee"]
        target_positions["front_right_abduction"] = joint_angles[LegName.FR]["abduction"]
        target_positions["front_right_hip"] = joint_angles[LegName.FR]["hip"]
        target_positions["front_right_knee"] = joint_angles[LegName.FR]["knee"]
        target_positions["back_left_abduction"] = joint_angles[LegName.BL]["abduction"]
        target_positions["back_left_hip"] = joint_angles[LegName.BL]["hip"]
        target_positions["back_left_knee"] = joint_angles[LegName.BL]["knee"]
        target_positions["back_right_abduction"] = joint_angles[LegName.BR]["abduction"]
        target_positions["back_right_hip"] = joint_angles[LegName.BR]["hip"]
        target_positions["back_right_knee"] = joint_angles[LegName.BR]["knee"]

        # Set all joints angles to zero to verify model matches expected zero positions of the inverse kinematics.
        for key in target_positions.keys():
            target_positions[key] = radians(45)

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

    input = Input()
    quad = Quad()

    joint_angles = None
    start = time.time()

    try:
        while simulation.is_running():
            step_start = time.time()

            ik_parameters = input.get_ik_parameters()

            base_foot_points = quad.get_base_foot_points()
            quad.set_body_pose_by_transform_inputs(ik_parameters, base_foot_points)

            if not quad.ik_error and not quad.joint_angle_error:
                joint_angles = quad.get_joint_angles(AngleUnits.RADIANS)
                # print(joint_angles)

            simulation.tick(joint_angles)

            # Delay between simulation steps.
            time_until_next_step = simulation.get_timestep() - (time.time() - step_start)
            if time_until_next_step > 0:
                time.sleep(time_until_next_step)

    except Exception as e:
        print(str(e))
        print(traceback.format_exc())

    finally:
        input.shutdown()
