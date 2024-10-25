# plot.py

Generates a wireframe 3D plot of a quadruped controlled by a gamepad to demonstrate and verify inverse kinematics and gaits.

# sim.py

Starts the MuJoCu physics simulation of the quadruped. 

# live.py

Executes on the quadruped's Raspberry Pi with a CAN shield to control quadrudped's motors based on gamepad inputs.

# zero_motors.py

Verify motor ID configurations, joint angle directions, and physical hardware. Allows setting the motor's driver's zero position.

After setting a new zero the displayed angle value reflect the zeroed position, however, the motor must be power cycled for the new zero value to take effect in motor's hardware driver. Executing motion scripts after setting a new zero and without power cycling the motors could result in a physical crash and cause damage.



