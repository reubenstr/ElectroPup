

## zero_motors.py

zero_motors.py is a tool to view live motor angles and zero individual motors.

After setting a new zero the displayed angle value will be offset to reflect the new angle. However, the motor must be power cycled for the new zero value to take effect in it's hardware driver. Executing motion scripts after setting a new zero and without power cycling the motors could result in a physical crash and cause damage.



