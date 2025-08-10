import time
import traceback
import mujoco
import mujoco.viewer
import numpy as np
from math import radians

from quadruped.interfaces import AngleUnits, LegName, JointName, MotionState
from quadruped.motion import Motion, Gait
from input.interfaces import InputCommand
from input.input import Input

"""
    Shows the quadruped in Mujoco simulation enviroment.

    Connect the gamepad (PS4) to pose and walk the quadruped.

    Some of the control logic (retricting motions states when motors are disabled) from the live 
    quadruped (main.py) are removed due to no physical hardware (motors).
"""

# np.set_printoptions(suppress=True)


class Main:
    def __init__(self):

        print(f"[Main] starting")

        self.input = Input(callback=self.controller_event_callback)
        self.motion = Motion()

        self.motion.set_target_motion_state(MotionState.WALK)

        self.simulation = Simulation()

    def controller_event_callback(self, event: InputCommand):

        if event is InputCommand.STAND:
            self.motion.set_target_motion_state(MotionState.STAND)
            self.motor_enable_flag = True

        if event is InputCommand.SIT:
            self.motion.set_target_motion_state(MotionState.SIT)

        if event is InputCommand.POSE:
            self.motion.set_target_motion_state(MotionState.POSE)

        if event is InputCommand.WALK:
            self.motion.set_target_motion_state(MotionState.WALK)

        if event is InputCommand.GAIT_WALK:
            self.motion.set_target_gait(Gait.CRAWL)

        if event is InputCommand.GAIT_TROT:
            self.motion.set_target_gait(Gait.TROT)

        print(f"[MAIN] Controller event received: {event.name}")

    def run(self):
        while self.simulation.is_running():

            step_start = time.time()

            self.motion.set_ik_parameters(self.input.get_ik_parameters())
            self.motion.set_motion_parameters(self.input.get_motion_parameters())

            if not self.motion.get_quad().get_ik_error() and not self.motion.get_quad().get_joint_angle_error():
                joint_angles = self.motion.get_quad().get_joint_angles(AngleUnits.RADIANS)
                # print(joint_angles)

                self.simulation.tick(joint_angles)

            # Delay between simulation steps.
            time_until_next_step = self.simulation.get_timestep() - (time.time() - step_start)
            if time_until_next_step > 0:
                time.sleep(time_until_next_step)

    def shutdown(self):
        self.input.shutdown()


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
        target_positions["front_left_abduction"] = joint_angles[LegName.FL][JointName.ABDUCTION]
        target_positions["front_left_hip"] = joint_angles[LegName.FL][JointName.HIP]
        target_positions["front_left_knee"] = joint_angles[LegName.FL][JointName.KNEE]
        target_positions["front_right_abduction"] = joint_angles[LegName.FR][JointName.ABDUCTION]
        target_positions["front_right_hip"] = joint_angles[LegName.FR][JointName.HIP]
        target_positions["front_right_knee"] = joint_angles[LegName.FR][JointName.KNEE]
        target_positions["back_left_abduction"] = joint_angles[LegName.BL][JointName.ABDUCTION]
        target_positions["back_left_hip"] = joint_angles[LegName.BL][JointName.HIP]
        target_positions["back_left_knee"] = joint_angles[LegName.BL][JointName.KNEE]
        target_positions["back_right_abduction"] = joint_angles[LegName.BR][JointName.ABDUCTION]
        target_positions["back_right_hip"] = joint_angles[LegName.BR][JointName.HIP]
        target_positions["back_right_knee"] = joint_angles[LegName.BR][JointName.KNEE]

        # Set all joints angles to zero to verify model matches expected zero positions of the inverse kinematics.
        #for key in target_positions.keys():
        #    target_positions[key] = radians(45)

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

    main = Main()

    try:
        main.run()
    except KeyboardInterrupt:
        print("Keyboard interrupt, exiting")
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
    finally:
        main.shutdown()
