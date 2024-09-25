#!/usr/bin/env python3

"""
    Create a 3D wire plot of a quadruped body and legs.
    Control the quadruped rotation and translation using a gamepad.
    
    Used to validate body frame, inverse kinematics, and pose input (gaits) prior to applying code to physicas simulations.
"""

import numpy as np
import matplotlib.pyplot as plt
from math import pi
from time import sleep

# Local source.
from model.body import Body
from GamepadInterface import GamepadInterface
from FrameParameters import FrameParameters
from MotionParameters import MotionParameters


###############################################################################
# Setup dependancies
###############################################################################

motion_parameters_filepath = "./parameters/motion_parameters.yaml"
frame_parameters_filepath = "./parameters/frame_parameters.yaml"
    
frame_parameters = FrameParameters(frame_parameters_filepath)
motion_parameters = MotionParameters(motion_parameters_filepath)

gamepad_interface = GamepadInterface(motion_parameters)
gamepad_interface.connect_gamepad()

body = Body(frame_parameters=frame_parameters)

###############################################################################
# Create the 3D plot
###############################################################################

fig = plt.figure()
ax = fig.add_subplot(projection='3d')

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

ax.set_xlim([-0.25, 0.25])
ax.set_ylim([0.0, 0.4])
ax.set_zlim([-0.2, 0.2])

ax.view_init(elev=-45,azim=45, roll=45)

plt.ion()
plt.show()


###############################################################################
# Update the plot
###############################################################################

while (True):
    for line in plt.gca().lines:       
        line.remove()

    motion_parameters = gamepad_interface.get_motion_parameters()

    body.set_body_transform_inputs(x=motion_parameters.side_translation,y=motion_parameters.height_translation,z=motion_parameters.forward_translation, phi=motion_parameters.roll, theta=motion_parameters.pitch, psi=motion_parameters.yaw)

    # Define absolute position for the legs
    # Below is default values.
    # Values can be updated by a gait to show trajectory.
    l = body.body_length
    w = body.body_width
    l1 = body.hip_length
    offset = -0.0
    desired_p4_points = np.array([ [-l/2,   0,  w/2 + l1 + offset],
                                [ l/2 ,  0,  w/2 + l1+ offset],
                                [ l/2 ,  0, -w/2 - l1- offset],
                                [-l/2 ,  0, -w/2 - l1- offset] ])

    body.set_absolute_foot_coordinates(desired_p4_points)

    coords = body.get_leg_coordinates()
 
    # Construct the body of 4 lines from the first point of each leg (the four corners of the body)
    for i in range(4):
        # For last leg, connect back to first leg point
        if i == 3:
            ind = -1
        else:
            ind = i        
        x_vals = [coords[ind][0][0], coords[ind+1][0][0]]
        y_vals = [coords[ind][0][1], coords[ind+1][0][1]]
        z_vals = [coords[ind][0][2], coords[ind+1][0][2]]
        ax.plot(x_vals,y_vals,z_vals,color='k')[0]

    # Plot color order for leg links: (hip, upper leg, lower leg)
    plt_colors = ['r','c','b']
    for leg in coords:
        for i in range(3):                    
            x_vals = [leg[i][0], leg[i+1][0]]
            y_vals = [leg[i][1], leg[i+1][1]]
            z_vals = [leg[i][2], leg[i+1][2]]
            ax.plot(x_vals,y_vals,z_vals,color=plt_colors[i])[0]
         
    fig.canvas.draw()
    fig.canvas.flush_events()
    
    sleep(0.010)