
# ElectroPup

A quadrudped robot dog!

# 🐶 About

<img src="https://github.com/reubenstr/ElectroPup/blob/main/images/electropup-cad-front-angle.png" width="800">

# 🕑 Status

Robot is posing live!

Documentation is a work in progress.

See TODO section for major tasks.

# 📁 Docs

See the docs directory for BOM, 3D printed parts, installation notes, actuator drivers, CAN drivers, etc.

# 🧮 Kinematics

<img src="https://github.com/reubenstr/ElectroPup/blob/main/images/electro-pup-wireframe-demo.gif" width="800">

The plot shows the robot's wireframe moving based on a gamepads input.

Inverse kinematics and plotting code was a sourced from mike4192: [https://github.com/mike4192/](https://github.com/mike4192/). This project added live plot updates from gamepad inputs and visual warnings for IK and joint range errors.

Run plot.py to start the plot. A gamepad is required to update the plot but if a gamepad is not connected the plot will display a static pose.

# ⏯ Simulation

<img src="https://github.com/reubenstr/ElectroPup/blob/main/images/electro-pup-mujuco-simulation-pose.png" width="800">

Simulation is performed in [MuJoCo](https://mujoco.org/).

Run ./sim.py to start the simulation (gamepad required to drive the robot, keyboard buttons not added yet)

# 🏋️ Motors

The motors are MG4010E-i10v3 actuators made by LingKong (LKMTECH) and can be purchased from [Aliexpress](https://www.aliexpress.us/item/3256805950420462.html?spm=a2g0o.order_list.order_list_main.5.32491802no3XMa&gatewayAdapt=glo2usa).

### Specifications
- voltage: 7.4-32v
- communication: CAN 1Mbps
- rated torque: 2.5 N.m
- max torque: 4.5 N.m
- rated current: 3.5 A
- max power: 140 W
- gear ratio: 1:10
- encoders: 18-bit motor, 14-bit reducer
- size: 53mm diameter, 41mm tall
- weight: 238 grams

See docs directory for more infomation.

### MG4010E-i10v3 Pros
- easy to use configuration software over UART with non-proprietary USB to UART hardware (Windows only however).
- readable CAN bus communication documentation
- small physical size that works well with the desired size of ElectroPup
- non-proprietary power/communications connector (JST-ZH 6-POS)

### MG4010E-i10v3 Cons
- closed source firmware
- foreign sourced and warranty process
- CAN unable to configure all parameters
- UART required to configure error thresholds, motor torque limits (for compliance), etc.
- some motors are more difficult to turn by hand and require slightly more operational current

### Other Options

There are other promising actuators on the market that are less expensive and may better fit some projects starting from scratch: [Xiaomi CyberGear](https://www.aliexpress.us/item/3256805896329964.html) and [Steadywin 5N.M GIM6010-8](https://www.aliexpress.us/item/3256806153022534.html). These motors have larger diameters, more weight, and require more power. The motor libraries for ElectroPup are not compatible, however here is noteable progress from the SimpleFOC community to add SimpleFOC firmware these motors [CyberGear discussion](https://community.simplefoc.com/t/xiaomi-cyber-dog-geared-motor-60/3855) and [Steadywin discussion](https://community.simplefoc.com/t/steadywin-new-cheap-gear-motor/4509).

### Motor Zero Positions

<img src="https://github.com/reubenstr/ElectroPup/blob/main/images/electro-pup-motors-in-zero-position.png" width="800">

### Motor Tags

<img src="https://github.com/reubenstr/ElectroPup/blob/main/images/electro-pup-motor-labels.png" width="800">

### Motor Calibration

<img src="https://github.com/reubenstr/ElectroPup/blob/main/images/electro-pup-zero-motors-script.png" width="800">

The zero-motors.py script is a quick way to verify correct motor configuration and zero the motors.

| State | Description |
| ------------- | ------------- |
| STBY | Motor found with on the associated CAN bus with and motor ID and has not been zeroed since the script started  |
| ZEROED  | Motor was zeroed  |
| ERROR | No communication with motor on the accociated the CAN bus and motor ID |

🚩 Motor zero does not take effect until the motor is power cycled. 🚩

The zero_motors.py script applies an offset after zeroing a motor as a convience to continue calibration without power cycling.

# ⚡ PCBs

There are two custom PCBs:
- **Power Carrier:** power and CAN bus distribution
- **Auxiliary Board:** LCD display and pheripherials

Boards are designed in [KiCad](https://www.kicad.org/) v8 and fabricated by JLCPCB.

### Power Carrier

<img src="https://github.com/reubenstr/ElectroPup/blob/main/images/electro-pup-power-carrier-v1-render.png" width="800">

The Power Carrier PCB provides a system on/off switch and distributes power the motor headers. Four CAN bus networks split the motors into separate legs, but ElectroPup uses jumpers to merge the front legs into a single network and the back legs into a single network.

### Auxiliary Board

<img src="https://github.com/reubenstr/ElectroPup/blob/main/images/electro-pup-auxiliary-board-v1-render.png" width="800">

Features:
- Powers RPi via terminal header
- LCD display
- Buzzer (variable pitch)
- NeoPixel strips
- RC Servo channel
- I2C expansion
- Button to control LCD and shutdown Rasperry Pi before power off

Provides direct connection to RPi header for the following breakouts:
- IMU (BNO055 via I2C)
- 4x contact inputs or GPIO
- I2S for sound driver (future barks 🐶)
- SBUS to use RC transmitter if BLE gamepad fails in RF conjected areas

The current version of the Auxiliary Board was designed to be quick to assemble (hence the STM32 dev board) to make the board more accessible for builders with non-advanced skills.

### Future Revisions

Future revisions for the PCBs in general may include adding a current sensor for the overall power draw and battery voltage level. Moving the isolated DC-DC from the Power Carrier to the Auxiliary Board.

# 🎮 Gamepad

<img src="https://github.com/reubenstr/ElectroPup/blob/main/images/electro-pup-gamepad-controls.png" width="800">

ElectroPup was coded with a PS4 controller in mind. But xBox, PS5, Logitech gamepads can also be used with minor software modifications in [gamepad.py](https://github.com/reubenstr/ElectroPup/blob/250d78c293b20c71e25bdc08a2818614014fc070/src/system/gamepad/gamepad.py) and [gamepad_inferface.py](https://github.com/reubenstr/ElectroPup/blob/250d78c293b20c71e25bdc08a2818614014fc070/src/system/gamepad/gamepad_interface.py#L404).

Future additions to the controller may include commands to flip the quadruped after a rollover, change gait, hop, bark, etc.

# 🚧 TODO  

### Major

- build and document battery pack
- implement gait controller and start walking
- update kinematics to include hip to foot x-axis offset
- finish IMU code
- implement machine learning to handle uneven terrian
- implement vision system (camera or LiDAR) for obstacle avoidance
- complete BOM and documentation

### Minor
- design foot bolt clips and install
- convert kinematics orientation from Z being forward to X being forward to match simulation
- add speaker for barks
- add a tail ੭ 
- rework NeoPixel strip brackets to include a light diffusing layer

### Future Possibilities
- add current sensor for entire system
- rework PCBs to move DC-DC from Power Carrier to Auxiliary Board

# 💻 Environment and IDEs 

There are three hardware/software enviroments described below.

### PC/Laptop - Plotting, Simulation, and Development

Desktop or laptop computer running Ubunut 22.04 Desktop. Newer Ubuntu versions or other distros are likely to work as well. 

Software: VSCode (with remote SSH extension), Drawio, LibreOffice, KiCad, OrcaSlicer, Chrome/Firefox

### Raspberry Pi - Quadruped Hardware Driver

The quadruped is driven by a Raspberry Pi 4 (2GB RAM, more may be required for advanced future features). A Raspberry Pi 5 should work but is untested (there are GPIO driver differences).

### STM32 - Auxiliary Board

A STM32F401 Black Pill dev kit operates the auxiliary board to display the quadruped motor and system status on a LCD display. 

Software: VSCode (with Platformio extension that loads libraries).

# ⚙️ Parts

The 3D printed parts are printed using Polymaker PolyMax Tough PLA that was selected for strength and ease of printing. See these excellent blog posts: [cnckitchen](https://www.cnckitchen.com/blog/the-difference-of-pla-and-pla-tested-feat-polymaker) and [edemargerie](https://www.instructables.com/Comparing-Impact-Resistance-of-21-Filaments-for-3D/).

| Item         | Estimated Print Time | Estimated Amount   |
|--------------|----------------------|--------------------|
| Main color   | 25.07 hours          | 738 grams          |
| Accent color | 3.53 hours           | 76 grams           |

### CAD

Parts are modeled using [OnShape](https://www.onshape.com/en/) which provides free web-based full access for non-commericial use.

### Links

All parts have export permissions to allow copying the workspace for modifications.

- [Assembly](https://cad.onshape.com/documents/b02341d4ebb7f3e9dd488186)
- [Legs](https://cad.onshape.com/documents/6da583196278caf8e90b3122)
- [Body](https://cad.onshape.com/documents/280c24f1b6bdbe8246159786)
- [Hips](https://cad.onshape.com/documents/428031d0c98bf15dcc9f5c8c)
- [Tools](https://cad.onshape.com/documents/3677b35bffbfedb5a3fd2b26)
- [Parts](https://cad.onshape.com/documents/6d4d4e21394ee725ee8ddb38)
- [PCB](https://cad.onshape.com/documents/c8a855826c37bd92b89d9f0e)
- [Neopixels](https://cad.onshape.com/documents/567292ac55c75b2efa25b7d5)

# 👏 Credits

There are many excellent open source quadruped robot projects at various sizes, costs, and complexity. Below are projects and code examples worth checking out.

- https://github.com/mit-biomimetics/Cheetah-Software
- https://github.com/mike4192/spotMicro
- https://github.com/mike4192/spot_micro_kinematics_python
- https://spotmicroai.readthedocs.io/en/latest/
- https://github.com/adham-elarabawy/open-quadruped
- https://github.com/chvmp/champ
- https://grabcad.com/library/diy-quadruped-robot-1
- https://github.com/Jerome-Graves/yertle
- https://www.youtube.com/@Jorgefer88
- https://github.com/reubenstr/zuko