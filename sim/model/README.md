# Readme

Generates quadruped inverse kinematics.
Creates wireframe plot of quadruped.
Gamepad controls rotation and translation of the plotted quadruped.

# Original Repository

Quadrupend inverse kinematics and wireframe from:
https://github.com/mike4192/spot_micro_kinematics_python

## Updates to Original Repository

Joint naming conventions changed to reflect naming conventions used in MuJoCo.
Added method to update rotation and translation using a single call.
Added frame parameters class to input frame dimensions and joint bounds.
Added joint bound check method.
Added custom exceptions for better error handling.
Added gamepad to control plot live.
Added frame and motion parameter files.
Changed method names removing references to spot to prefer more generic naming.

### TODO

Rotate coordinate convention to match MuJoCo (swap Y and Z)
