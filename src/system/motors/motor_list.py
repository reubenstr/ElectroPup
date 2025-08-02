from typing import List

from motors.interfaces import MotorInfo, MotorName
from quadruped.parameters.frame_parameters import FrameParameters

"""
    Motor configurations.

    Use allow_motion and allow_comms during development to limit active motors and comms errors.

"""


def motor_list() -> List[MotorInfo]:
    fp = FrameParameters()

    return [
        MotorInfo(
            name=MotorName.FLA,
            can_channel="can0",
            id=1,
            min_angle=fp.abduction_joint_lower_bounds,
            max_angle=fp.abduction_joint_upper_bounds,
            inverse_rotation=True,
            allow_motion=True,
            allow_comms=True,
        ),
        MotorInfo(
            name=MotorName.FLH,
            can_channel="can0",
            id=2,
            min_angle=fp.hip_joint_lower_bounds,
            max_angle=fp.hip_joint_upper_bounds,
            inverse_rotation=True,
            allow_motion=True,
            allow_comms=True,
        ),
        MotorInfo(
            name=MotorName.FLK,
            can_channel="can0",
            id=3,
            min_angle=fp.knee_joint_lower_bounds,
            max_angle=fp.knee_joint_upper_bounds,
            inverse_rotation=True,
            allow_motion=True,
            allow_comms=True,
        ),
        MotorInfo(
            name=MotorName.FRA,
            can_channel="can0",
            id=4,
            min_angle=fp.abduction_joint_lower_bounds,
            max_angle=fp.abduction_joint_upper_bounds,
            inverse_rotation=False,
            allow_motion=True,
            allow_comms=True,
        ),
        MotorInfo(
            name=MotorName.FRH,
            can_channel="can0",
            id=5,
            min_angle=fp.hip_joint_lower_bounds,
            max_angle=fp.hip_joint_upper_bounds,
            inverse_rotation=True,
            allow_motion=True,
            allow_comms=True,
        ),
        MotorInfo(
            name=MotorName.FRK,
            can_channel="can0",
            id=6,
            min_angle=fp.knee_joint_lower_bounds,
            max_angle=fp.knee_joint_upper_bounds,
            inverse_rotation=True,
            allow_motion=True,
            allow_comms=True,
        ),
        MotorInfo(
            name=MotorName.BLA,
            can_channel="can1",
            id=1,
            min_angle=fp.abduction_joint_lower_bounds,
            max_angle=fp.abduction_joint_upper_bounds,
            inverse_rotation=False,
            allow_motion=True,
            allow_comms=True,
        ),
        MotorInfo(
            name=MotorName.BLH,
            can_channel="can1",
            id=2,
            min_angle=fp.hip_joint_lower_bounds,
            max_angle=fp.hip_joint_upper_bounds,
            inverse_rotation=True,
            allow_motion=True,
            allow_comms=True,
        ),
        MotorInfo(
            name=MotorName.BLK,
            can_channel="can1",
            id=3,
            min_angle=fp.knee_joint_lower_bounds,
            max_angle=fp.knee_joint_upper_bounds,
            inverse_rotation=True,
            allow_motion=True,
            allow_comms=True,
        ),
        MotorInfo(
            name=MotorName.BRA,
            can_channel="can1",
            id=4,
            min_angle=fp.abduction_joint_lower_bounds,
            max_angle=fp.abduction_joint_upper_bounds,
            inverse_rotation=True,
            allow_motion=True,
            allow_comms=True,
        ),
        MotorInfo(
            name=MotorName.BRH,
            can_channel="can1",
            id=5,
            min_angle=fp.hip_joint_lower_bounds,
            max_angle=fp.hip_joint_upper_bounds,
            inverse_rotation=True,
            allow_motion=True,
            allow_comms=True,
        ),
        MotorInfo(
            name=MotorName.BRK,
            can_channel="can1",
            id=6,
            min_angle=fp.knee_joint_lower_bounds,
            max_angle=fp.knee_joint_upper_bounds,
            inverse_rotation=True,
            allow_motion=True,
            allow_comms=True,
        ),
    ]
