# ElectroPup

<img src="images/electro-pup-standing.jpg" width="800">

ElectroPup is a DIY 3D-printed quadruped robot using 'low cost' BLDC motors.


[Video of kinematic poses](videos/electro-pup-posing.mp4)

[Video of walking, turning, strafing](videos/electro-pup-in-motion.mp4")

## Basic Specifications

- RPi 5
- 12x BLDC motors
- Auxiliary board w/LCD display
- 9-axis accelerometer/gyro sensor
- 6s Li-Ion battery, ~72wH
- 4.5kg

ElectroPup's control system is coded in Python. For a ROS2 based quadruped, see my previous project [Zuko](https://github.com/reubenstr/zuko).

---

# Docs

See the docs directory for a setup guide, bill of materials (BOM), 3D printed parts info, and miscellaneous design notes.

---

# UI

<img src="images/electro-pup-ui-live.png" width="800">

The UI shows the status of the entire system: quadruped joint positions, subsystem status, motor information, inputs, sensors, loop times, etc. The above image shows the simulated quadruped overlapped with real quadruped (based on motor feedback).

<img src="images/electro-pup-ui-sim.png" width="800">

The above image shows a virtual circle the feet follow to walk in a circle and the bezier curves used for moving the feet up and down.

The UI is built from the React Native Framework using Expo and runs on web. The app will run on Android without the plot. The entire system runs in dev mode so you can run the simulation and UI from a development PC without physical hardware.

---

# Kinematics

<img src="images/electro-pup-wireframe-demo.gif" width="800">

Inverse kinematics, leg position, and gamepad inputs are verified using the UI.


### Trajectories

Bezier curves, sin arcs, and curvature projection are used to generate trajectories. The plots below are examples of control points configurations. 

<img src="images/beizer-control-points-chart.png" width="800">

The output of `./src/plot/bezier_curve_plot.py`

Rotation is achieved by projecting a linear trajectory onto a curve. The plots are of example projection calculations.

<img src="images/arc-projection-chart.png" width="800">

The output of `./src/plot/projection_plot.py`


# Simulation

<img src="images/electro-pup-mujuco-simulation-pose.png" width="800">

Simulation is performed in [MuJoCo](https://mujoco.org/) and can be started by running `./src/sim.sh`. Currently, input controlls are only provided by the gamepad. The `ElectroPup.xml` currently does not have approximate masses or inertial so the simulated quadruped is rather bouncy.

---

# Electronics

<img src="images/electro-pup-lcd-and-electronics.jpg" width="800">

## PCBs

PCBs are designed in [KiCad](https://www.kicad.org/) v8 and fabricated by JLCPCB.

### Power Carrier

<img src="images/electro-pup-power-carrier-v1-render.png" width="800">

The Power Carrier PCB provides a main on/off power switch and distributes power to the motor headers. The Power Carrier creates four CAN bus networks one for each leg. Solder jumpers allow merging the front two legs into a single network and the back two legs into another single network.

### Auxiliary Board

<img src="images/electro-pup-auxiliary-board-v1-render.png" width="800">

The auxiliary board is optional and not required for the quadruped to operate.

Features:
- Powers RPi via terminal header
- LCD display
- Buzzer (variable pitch)
- NeoPixel strips
- RC Servo channel
- I2C expansion
- Button to control LCD and shutdown Raspberry Pi before power off

Provides direct connection to RPi header for the following breakouts:
- IMU (BNO055 via I2C)
- 4x contact inputs or GPIO
- I2S for sound driver (future barks 🐶)
- SBUS to use RC transmitter if BLE gamepad fails in RF congested areas

# Motors

The motors are MG4010E-i10v3 actuators made by LingKong (LKMTECH) and can be purchased from [Aliexpress](https://www.aliexpress.us/item/3256805950420462.html?spm=a2g0o.order_list.order_list_main.5.32491802no3XMa&gatewayAdapt=glo2usa).

### Specifications
- voltage: 7.4-32V
- communication: CAN 1Mbps
- rated torque: 2.5 N.m
- max torque: 4.5 N.m
- rated current: 3.5 A
- max power: 140 W
- gear ratio: 1:10
- encoders: 18-bit motor, 14-bit reducer
- size: 53mm diameter, 41mm tall
- weight: 238 grams

### MG4010E-i10v3 Pros
- easy to use configuration software over non-proprietary USB to UART hardware
- readable CAN bus communication documentation
- small physical size that works well with the desired frame size of ElectroPup
- non-proprietary power/communications connector (JST-ZH 6-POS)

### MG4010E-i10v3 Cons
- configuration software is Windows only
- closed source firmware
- foreign sourced, complicating the warranty process
- CAN unable to configure all parameters
- UART required to configure error thresholds, motor torque limits (for compliance), etc.
- some motors are more difficult to turn by hand and require slightly more operational current

Future projects will prioritize ODrive compatible drivers.


### Motor Zero Positions

<img src="images/electro-pup-motors-in-zero-position.png" width="800">

### Motor Tags

<img src="images/electropup-cad-topdown-motor-tags.png" width="800">

### Motor Calibration

<img src="images/electro-pup-zero-motors-script.png" width="800">

The zero-motors.py script is a quick way to verify correct motor configuration and to zero the motors.

# CAN Bus

<img src="images/electro-pup-can-bus-controller.png" width="800">

The CAN bus controller is a [2-Channel Isolated CAN Expansion HAT](https://www.waveshare.com/2-ch-can-hat.htm) from waveshare.

Each CAN controller drives six motors with an average motor update rate of ~70 Hz. This includes fetching encoder position, setting target angle/speed, and getting error states.

# Gamepad

<img src="images/electro-pup-gamepad-controls.png" width="800">

ElectroPup was coded with a PS4 controller in mind, however xBox, PS5, Logitech gamepads may be used with minor software modifications.

---

# Environment and IDEs 

There are three hardware/software environments described below.

### PC/Laptop - Plotting, Simulation, and Development

Desktop or laptop computer running Ubuntu Desktop (or your preferred flavor of Linux).

Software: VSCode (with remote SSH and PlatformIO extensions), Drawio, LibreOffice, KiCad, OrcaSlicer, Chrome/Firefox


### Raspberry Pi - Quadruped Hardware Driver

The quadruped compute is a Raspberry Pi 5.

The OS is Raspberry Pi OS Lite (Bookworm 64-bit), which is headless, so all development is performed using remote SSH.

### STM32 - Auxiliary Board

An STM32F401 Black Pill dev kit operates the auxiliary board to display the motor and system status on a LCD display and interface with other peripherals such as the buzzer. 

Uses VSCode with PlatformIO on the PC/Laptop for development.

# Parts

The 3D printed parts are printed using Polymaker PolyMax Tough PLA selected for strength and ease of printing. See these excellent blog posts for more information: [cnckitchen](https://www.cnckitchen.com/blog/the-difference-of-pla-and-pla-tested-feat-polymaker) and [edemargerie](https://www.instructables.com/Comparing-Impact-Resistance-of-21-Filaments-for-3D/).

| Color          | Estimated Print Time | Estimated Filament |
| -------------- | -------------------- | ------------------ |
| main (red)     | 25.23 hours          | 742 grams          |
| accent (black) | 3.58 hours           | 92 grams           |

### CAD

<img src="images/electropup-cad-front-angle.png" width="800">

Parts are modeled using [OnShape](https://www.onshape.com/en/) which provides free web-based full access for non-commercial use. The links below should have export permissions to allow copying the workspace.

- [Assembly](https://cad.onshape.com/documents/b02341d4ebb7f3e9dd488186)
- [Legs](https://cad.onshape.com/documents/6da583196278caf8e90b3122)
- [Body](https://cad.onshape.com/documents/280c24f1b6bdbe8246159786)
- [Hips](https://cad.onshape.com/documents/428031d0c98bf15dcc9f5c8c)
- [Tools](https://cad.onshape.com/documents/3677b35bffbfedb5a3fd2b26)
- [Parts](https://cad.onshape.com/documents/6d4d4e21394ee725ee8ddb38)
- [PCB](https://cad.onshape.com/documents/c8a855826c37bd92b89d9f0e)
- [Neopixels](https://cad.onshape.com/documents/567292ac55c75b2efa25b7d5)

# Battery Pack 

The battery is a custom 6S1P Li-Ion using 18650s with a load balancing BMS. The 18650's are Sanyo branded and rated at 3250mAH each providing an estimated 72Wh.

<img src="images/electro-pup-battery-pack-progress-1.jpg" width="800">

The above image is showing work in progress. The [insulation rings](https://imrbatteries.com/products/18650-terminal-insulators-fish-paper-20pcs-green-round-rings) were forgotten during fabrication and really should be mandatory for any battery build. 

<img src="images/electro-pup-battery-pack-progress-2.jpg" width="800">

The BMS is a HXYP-6S-CW15.

---

# Future Improvements  

This is a general improvement list for future updates or revisions. 

- add upside down control (the frame supports walking even after flipped)
- apply IMU for smoother gaits
- add center of mass calculations for smoother gaits
- swap battery and RPi positions for better center of mass
- swap foot lag bolt from SAE to metric
- add curvature to lower leg
- add speaker for barks
- add a tail
- add voltage/current sensor (such as an INA228)
- remove STM32 from aux board and use RPI directly for buzzer, LCD, etc.
- create a [MPC](https://en.wikipedia.org/wiki/Model_predictive_control) controller

# Thoughts

Due to a lower power consumption than estimated, a larger frame and longer legs can be created. A larger frame would support moving the knee motor to the hip area allowing the lower leg to be belt driven. The reduction of mass of the knee will increase center of mass stability and create smoother gaits.

Future Auxiliary board revisions will remove the STM32 and either drive the LCD directly from the RPi or remove it completely. The extra complexity outweighs the LCD's usefulness, especially when the GUI provides significantly more data.

Future power carrier PCB revisions will include a voltage/current sensor such as a INA228 and a fuse.

The carbon rods twist during the run gait which can be reduced by extending the rods through the hip plates and adding face / butt plates. 

Future revisions will prioritize adding contact sensors that will allow for better terrain handling and future AI training.

# Questions

For any questions please post a new [issue](https://github.com/reubenstr/ElectroPup/issues) on the repo's GitHub page.

# Credits

Inverse kinematics and leg points for plotting were sourced from mike4192: [https://github.com/mike4192/](https://github.com/mike4192/).

Using carbon fiber tube as frame supports inspired from [Open Dog 3](https://www.youtube.com/watch?v=ts2l_Em7fpI&list=PLpwJoq86vov8uTgd8_WNgBHFpDYemO-OJ&index=3) by James Bruton.

There are many excellent open source quadruped robot projects at various sizes, costs, and complexity. Below are projects and code examples worth checking out.

- https://github.com/mit-biomimetics/Cheetah-Software
- https://github.com/mike4192/spotMicro
- https://github.com/mike4192/spot_micro_kinematics_python
- https://spotmicroai.readthedocs.io/en/latest/
- https://github.com/adham-elarabawy/open-quadruped
- https://www.youtube.com/jamesbruton
- https://github.com/chvmp/champ
- https://grabcad.com/library/diy-quadruped-robot-1
- https://github.com/Jerome-Graves/yertle
- https://www.youtube.com/@Jorgefer88
- https://www.youtube.com/watch?v=oYnsCE2H6ss
- https://github.com/JackDemeter/quadruped-robot
- https://github.com/reubenstr/zuko

---

# AI Disclosure

Project concept, aesthetic, engineering design, and original code base were conceived and executed by the author.

Portions of this codebase were reviewed, revised, and written with the assistance of Claude Code (Anthropic).
