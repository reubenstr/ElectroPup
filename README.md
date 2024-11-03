
# ElectroPup

A quadrudped robot dog!

## About

<img src="https://github.com/reubenstr/ElectroPup/blob/main/images/electropup-cad-front-angle.png" width="800">

## Docs

See the docs directory for installation notes, BOM, 3D printed parts info, actuator drivers, CAN drivers, etc.

## Kinematics

<img src="https://github.com/reubenstr/ElectroPup/blob/main/images/electro-pup-wireframe-demo.gif" width="800">

The plot shows the robot's wireframe moving based on a gamepads input.

Inverse kinematics and plotting code was a sourced from mike4192: [https://github.com/mike4192/](https://github.com/mike4192/). This project added live plot updates from gamepad inputs and visual warnings for IK and joint range errors.


## Simulation

<img src="https://github.com/reubenstr/ElectroPup/blob/main/images/electro-pup-mujuco-simulation-pose.png" width="800">

Simulation is performed in [MuJoCo](https://mujoco.org/).

## Motors

The motors are MG4010E-i10v3 actuators made by LingKong (LKMTECH).

<figure>
  <img src="https://github.com/reubenstr/ElectroPup/blob/main/images/electro-pup-motors-in-zero-position.png" alt="">
  <figcaption>Zero positions</figcaption>
</figure>

<img src="https://github.com/reubenstr/ElectroPup/blob/main/images/electro-pup-motors-in-zero-position.png" width="800">

Zero Position


<img src="https://github.com/reubenstr/ElectroPup/blob/main/images/electro-pup-motor-labels.png" width="800">

## PCBs

<img src="https://github.com/reubenstr/ElectroPup/blob/main/images/electro-pup-power-carrier-v1-render.png" width="800">

<img src="https://github.com/reubenstr/ElectroPup/blob/main/images/electro-pup-auxiliary-board-v1-render.png.png" width="800">


# TODO

Major TODO list:
- Implement gait controller and start walking
- Implement machine learning to handle uneven terrian
- Implement vision system (camera or LiDAR) for obstacle avoidance
- Complete BOM and documentation


# Environment and IDEs

There are three harware/software enviroments:
- **PC:** plotting, simulation, and development
- **Raspberry Pi:** quadruped hardware driver
- **STM32:** auxiliary board

### PC - Plotting, Simulation, and Development

Desktop or laptop PC running Ubunut 22.04 Desktop. Newer Ubuntu versions or other distros are likely to work as well. 

Software: VSCode (with remote SSH extension), Drawio, LibreOffice, KiCad, OrcaSlicer, Chrome/Firefox

### Raspberry Pi - Quadruped Hardware Driver

The quadruped is driven by a Raspberry Pi 4 with 2GB RAM. A Raspberry Pi 5 should work but is untested (there are pin driver differences).

### STM32 - Auxiliary Board

A STM32F401 Black Pill dev kit operates the auxiliary board to display the quadruped motor and system status on a LCD display. 

Software: VSCode (with Platformio extension that loads libraries).


# Parts

The 3D printed parts are printed from Polymaker PolyMax Tough PLA in red selected for strength and ease of printing. See [cnckitchen](https://www.cnckitchen.com/blog/the-difference-of-pla-and-pla-tested-feat-polymaker)'s excellent blog post.

Estimated amount of filament (main color): 738 grams

Estimated print time (main color): 25.07 hours.

### CAD

Parts are modeled using [OnShape](https://www.onshape.com/en/) which provides free web-based full access for non-commericial use.

### Links

All parts have export permissions to allow printing and modification.

- [Assembly](https://cad.onshape.com/documents/b02341d4ebb7f3e9dd488186)
- [Legs](https://cad.onshape.com/documents/6da583196278caf8e90b3122)
- [Body](https://cad.onshape.com/documents/280c24f1b6bdbe8246159786)
- [Hips](https://cad.onshape.com/documents/428031d0c98bf15dcc9f5c8c)
- [Tools](https://cad.onshape.com/documents/3677b35bffbfedb5a3fd2b26)
- [Parts](https://cad.onshape.com/documents/6d4d4e21394ee725ee8ddb38)
- [PCB](https://cad.onshape.com/documents/c8a855826c37bd92b89d9f0e)
- [Neopixels](https://cad.onshape.com/documents/567292ac55c75b2efa25b7d5)

# Credits

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