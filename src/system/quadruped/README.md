# Quadruped

Generates quadruped inverse kinematics.
Provides body and leg end points to generate lines on a 3D plot.

# Original Repository

Core quadruped inverse kinematics and wireframe from:
https://github.com/mike4192/spot_micro_kinematics_python

## Updates to Original Repository

- Joint naming conventions changed to reflect naming conventions used in MuJoCo.
- Added method to update rotation and translation using a single call.
- Added frame parameters class to input frame dimensions and joint bounds.
- Added joint bound check method.
- Added custom exceptions for better error reporting.
- Added frame and motion parameter files.
- Changed method names removing references to spot to prefer more generic naming.

### TODO

- Add gaits.
- Rotate coordinate convention to match MuJoCo (swap Y and Z).
- Fix needed to swap rotation and translation order when creating homogenous transformation (original code causes quadruped to lean instead of roll). Swap causes unit tests to fail.
- Add limits preventing knee joints from penetrating world floor.