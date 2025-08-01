# Details

Date : 2025-08-01 12:38:12

Directory /home/pc/Desktop/projects/ElectroPup/src/system

Total : 46 files,  4606 codes, 1262 comments, 1251 blanks, all 7119 lines

[Summary](results.md) / Details / [Diff Summary](diff.md) / [Diff Details](diff-details.md)

## Files
| filename | language | code | comment | blank | total |
| :--- | :--- | ---: | ---: | ---: | ---: |
| [src/system/\_\_init\_\_.py](/src/system/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [src/system/auxiliary/README.md](/src/system/auxiliary/README.md) | Markdown | 13 | 0 | 12 | 25 |
| [src/system/auxiliary/aux.py](/src/system/auxiliary/aux.py) | Python | 117 | 21 | 38 | 176 |
| [src/system/auxiliary/crc32.py](/src/system/auxiliary/crc32.py) | Python | 12 | 0 | 3 | 15 |
| [src/system/auxiliary/heartbeat.py](/src/system/auxiliary/heartbeat.py) | Python | 15 | 9 | 6 | 30 |
| [src/system/auxiliary/install\_heartbeat.sh](/src/system/auxiliary/install_heartbeat.sh) | Shell Script | 25 | 5 | 8 | 38 |
| [src/system/forwarder.py](/src/system/forwarder.py) | Python | 156 | 29 | 40 | 225 |
| [src/system/gamepad/\_\_init\_\_.py](/src/system/gamepad/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [src/system/gamepad/gamepad.py](/src/system/gamepad/gamepad.py) | Python | 180 | 34 | 45 | 259 |
| [src/system/gamepad/gamepad\_interface.py](/src/system/gamepad/gamepad_interface.py) | Python | 446 | 63 | 53 | 562 |
| [src/system/gamepad/moving\_average.py](/src/system/gamepad/moving_average.py) | Python | 11 | 0 | 3 | 14 |
| [src/system/hardware/bno055\_driver.py](/src/system/hardware/bno055_driver.py) | Python | 93 | 20 | 32 | 145 |
| [src/system/hardware/hardware.py](/src/system/hardware/hardware.py) | Python | 187 | 27 | 64 | 278 |
| [src/system/hardware/i2c\_scanner.py](/src/system/hardware/i2c_scanner.py) | Python | 21 | 7 | 7 | 35 |
| [src/system/hardware/ina228\_driver.py](/src/system/hardware/ina228_driver.py) | Python | 308 | 129 | 80 | 517 |
| [src/system/input/gamepad.py](/src/system/input/gamepad.py) | Python | 165 | 31 | 55 | 251 |
| [src/system/input/gamepad\_interface.py](/src/system/input/gamepad_interface.py) | Python | 449 | 62 | 52 | 563 |
| [src/system/input/input.py](/src/system/input/input.py) | Python | 45 | 12 | 17 | 74 |
| [src/system/input/touch.py](/src/system/input/touch.py) | Python | 106 | 13 | 30 | 149 |
| [src/system/interfaces.py](/src/system/interfaces.py) | Python | 66 | 1 | 25 | 92 |
| [src/system/motors/\_\_init\_\_.py](/src/system/motors/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [src/system/motors/can\_interface.py](/src/system/motors/can_interface.py) | Python | 195 | 55 | 39 | 289 |
| [src/system/motors/interfaces.py](/src/system/motors/interfaces.py) | Python | 41 | 0 | 9 | 50 |
| [src/system/motors/motor.py](/src/system/motors/motor.py) | Python | 223 | 45 | 45 | 313 |
| [src/system/motors/motor\_list.py](/src/system/motors/motor_list.py) | Python | 37 | 6 | 7 | 50 |
| [src/system/motors/motors.py](/src/system/motors/motors.py) | Python | 341 | 57 | 77 | 475 |
| [src/system/quadruped/\_\_init\_\_.py](/src/system/quadruped/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [src/system/quadruped/exceptions.py](/src/system/quadruped/exceptions.py) | Python | 4 | 8 | 1 | 13 |
| [src/system/quadruped/gait\_planner.py](/src/system/quadruped/gait_planner.py) | Python | 61 | 19 | 20 | 100 |
| [src/system/quadruped/interfaces.py](/src/system/quadruped/interfaces.py) | Python | 17 | 0 | 6 | 23 |
| [src/system/quadruped/kinematics.py](/src/system/quadruped/kinematics.py) | Python | 44 | 165 | 36 | 245 |
| [src/system/quadruped/leg.py](/src/system/quadruped/leg.py) | Python | 65 | 55 | 27 | 147 |
| [src/system/quadruped/motion.py](/src/system/quadruped/motion.py) | Python | 317 | 32 | 91 | 440 |
| [src/system/quadruped/parameters/frame\_parameters.py](/src/system/quadruped/parameters/frame_parameters.py) | Python | 16 | 12 | 11 | 39 |
| [src/system/quadruped/parameters/ik\_parameters.py](/src/system/quadruped/parameters/ik_parameters.py) | Python | 41 | 21 | 18 | 80 |
| [src/system/quadruped/parameters/motion\_parameters.py](/src/system/quadruped/parameters/motion_parameters.py) | Python | 47 | 28 | 20 | 95 |
| [src/system/quadruped/parameters/poses.py](/src/system/quadruped/parameters/poses.py) | Python | 19 | 0 | 2 | 21 |
| [src/system/quadruped/parameters/utilities.py](/src/system/quadruped/parameters/utilities.py) | Python | 15 | 0 | 7 | 22 |
| [src/system/quadruped/point.py](/src/system/quadruped/point.py) | Python | 178 | 49 | 96 | 323 |
| [src/system/quadruped/quad.py](/src/system/quadruped/quad.py) | Python | 164 | 76 | 42 | 282 |
| [src/system/quadruped/trajectory\_planner.py](/src/system/quadruped/trajectory_planner.py) | Python | 110 | 31 | 29 | 170 |
| [src/system/quadruped/transformations.py](/src/system/quadruped/transformations.py) | Python | 31 | 125 | 28 | 184 |
| [src/system/quadruped/transition\_planner.py](/src/system/quadruped/transition_planner.py) | Python | 91 | 8 | 21 | 120 |
| [src/system/status.py](/src/system/status.py) | Python | 74 | 0 | 33 | 107 |
| [src/system/utilities/key\_converter.py](/src/system/utilities/key_converter.py) | Python | 18 | 2 | 3 | 23 |
| [src/system/utilities/utilities.py](/src/system/utilities/utilities.py) | Python | 42 | 5 | 9 | 56 |

[Summary](results.md) / Details / [Diff Summary](diff.md) / [Diff Details](diff-details.md)