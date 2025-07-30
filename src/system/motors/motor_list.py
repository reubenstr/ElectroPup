
from typing import List

from system.motors.interfaces import MotorInfo, MotorName
from system.quadruped.parameters.frame_parameters import FrameParameters


def motor_list() -> List[MotorInfo]:
    fp = FrameParameters()

    return [
        MotorInfo(
            name=MotorName.FLA,
            can_channel="can0",
            id=1,
            min_angle=fp.abduction_joint_lower_bounds,
            max_angle=fp.abduction_joint_upper_bounds,
            inverse_rotation=False,     
            allow_motion=True,
            allow_comms=True,
        ),
         MotorInfo(
            name=MotorName.FLH,
            can_channel="can0",
            id=2,
            min_angle=fp.hip_joint_lower_bounds,
            max_angle=fp.hip_joint_upper_bounds,
            inverse_rotation=False,     
            allow_motion=False,
            allow_comms=False,
        ),
         MotorInfo(
            name=MotorName.FLK,
            can_channel="can0",
            id=3,
            min_angle=fp.knee_joint_lower_bounds,
            max_angle=fp.knee_joint_upper_bounds,
            inverse_rotation=False,     
            allow_motion=False,
            allow_comms=False,
        ),


    ]