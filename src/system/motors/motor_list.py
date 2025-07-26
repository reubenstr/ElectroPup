
from typing import List
from interfaces import MotorInfo

from frame_parameters import FrameParameters

def motor_list() -> List[MotorInfo]:
    fp = FrameParameters()

    # motor_tags = ["FLA", "FLH", "FLK", "FRA", "FRH", "FRK"] 
    # motor_tags_back = ["BLA", "BLH", "BLK", "BRA", "BRH", "BRK"]

    return [
        MotorInfo(
            name="FLA",
            can_channel="can0",
            id=1,
            min_angle=fp.abduction_joint_lower_bounds,
            max_angle=fp.abduction_joint_upper_bounds,
            inverse_rotation=False,     
            allow_motion=True,
            allow_comms=True,
        ),


    ]