# Model

ElectroPup model for MuJoCo physics simulation application.

Use the gamepad (PS4) to pose and walk the quadruped.

See assets folder for links to CAD models.

## Installation

Install MuJoCo (tested on Ubunut 22.04):
>pip3 install mujoco

## Execution

Run Mujoco application without specifying a model:
> python3 -m mujoco.viewer

Run Mujoco with the ElectroPup model (model only, no user input):
>python3 -m mujoco.viewer --mjcf=./scene.xml 

Run Mujoco with the ElectroPup model and Gamepad input:
>cd ~/ElectroPup/src/

>sim.sh


## Docs

https://mujoco.readthedocs.io/en/stable/APIreference/index.html


