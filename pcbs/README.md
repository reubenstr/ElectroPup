# PCBs

PCBs are designed in [KiCad](https://www.kicad.org/) (v8)

Custom libraries used for these projects may be found on my github repo: [https://github.com/reubenstr/kicad-libraries](https://github.com/reubenstr/kicad-libraries)

See the notes.txt in each project for next revision error fixes.


## Auxiliary Board

This board uses a STM32 co-processor to add the following functionality to the system:

- LCD display for error indication and status such as battery levels
- 1x buzzer
- 2x Neopixel strips
- 1x RC servo
- 1x button

This board also provides the following Raspberry Pi connection breakouts:
- BNO055 IMU
- SBUS FrSKY RC receiver input
- I2S header
- 4x contact switches (or aux GPIO)

## Power Carrier

This board provides the following functionality:
- Power distribution for the actuators
- CAN bus networks for the actuators
- Isolated DC-DC for the Raspberry Pi
- Main power On/Off switch
- Battery holder and power connection
