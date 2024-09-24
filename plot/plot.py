#!/usr/bin/env python3

"""
    Create a 3D wire plot of a quadruped body and legs.
    Control the quadruped rotation and translation using a gamepad.
    
    Used to validate body frame, inverse kinematics, and pose input (gaits) prior to applying code to physicas simulations.
"""

import os
import yaml
import numpy as np
import matplotlib.pyplot as plt
#import mpl_toolkits.mplot3d.axes3d as p3
from math import pi
from time import sleep

# Local source.

from model.body import Body
from GamepadInterface import GamepadInterface
from FrameParameters import FrameParameters


motion_parameters_filepath = "./parameters/motion_parameters.yaml"
frame_parameters_filepath = "./parameters/frame_parameters.yaml"       
    

frame_parameters = FrameParameters(frame_parameters_filepath)

if os.path.exists(motion_parameters_filepath):
    with open(motion_parameters_filepath, 'r') as stream:
        motion_parameters = yaml.safe_load(stream)
else:
    print(f"[Commander] parameter file not found! {motion_parameters_filepath}")



gamepad_interface = GamepadInterface(motion_parameters)
gamepad_interface.connect_gamepad()

d2r = pi/180
r2d = 180/pi


# Create a 3D figure
fig = plt.figure()
ax = fig.add_subplot(projection='3d')

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

# Set limits for axes
ax.set_xlim([-0.25, 0.25])
ax.set_ylim([0.0, 0.4])
ax.set_zlim([-0.2, 0.2])

# Set the starting view of the plot
ax.view_init(elev=-45,azim=45, roll=45)





body = Body(frame_parameters=frame_parameters)

# Define absolute position for the legs
l = body.body_length
w = body.body_width
l1 = body.hip_length
l2 = body.upper_leg_length
l3 = body.lower_leg_length
desired_p4_points = np.array([ [-l/2,   0,  w/2 + l1],
                               [ l/2 ,  0,  w/2 + l1],
                               [ l/2 ,  0, -w/2 - l1],
                               [-l/2 ,  0, -w/2 - l1] ])

body.set_absolute_foot_coordinates(desired_p4_points)

# Set a pitch angle
body.set_body_angles(theta=00*d2r)

# Get leg coordinates
coords = body.get_leg_coordinates()

# Initialize empty list top hold line objects
lines = []

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
    lines.append(ax.plot(x_vals,y_vals,z_vals,color='k')[0])

# Plot color order for leg links: (hip, upper leg, lower leg)
plt_colors = ['r','c','b']
for leg in coords:
    for i in range(3):
                
        x_vals = [leg[i][0], leg[i+1][0]]
        y_vals = [leg[i][1], leg[i+1][1]]
        z_vals = [leg[i][2], leg[i+1][2]]
        lines.append(ax.plot(x_vals,y_vals,z_vals,color=plt_colors[i])[0])


plt.ion()
plt.show()


while (True):

    motion_inputs = gamepad_interface.get_motion_inputs()

    ##sm.set_body_angles(phi=roll,theta=pitch,psi=yaw)

    swap = motion_inputs.y_translation
    motion_inputs.y_translation = motion_inputs.z_translation
    motion_inputs.z_translation = swap

    body.set_body_transform_inputs(x=motion_inputs.x_translation,y=motion_inputs.y_translation,z=motion_inputs.z_translation, phi=motion_inputs.roll, theta=motion_inputs.pitch, psi=motion_inputs.yaw)


    coords = body.get_leg_coordinates()

    # Construct the body of 4 lines from the first point of each leg (the four corners of the body)
    for line_index in range(4):
        # For last leg, connect back to first leg point
        if line_index == 3:
            ind = -1
        else:
            ind = line_index
    
        x_vals = [coords[ind][0][0], coords[ind+1][0][0]]
        y_vals = [coords[ind][0][1], coords[ind+1][0][1]]
        z_vals = [coords[ind][0][2], coords[ind+1][0][2]]
        lines[line_index].set_data(x_vals,y_vals)
        lines[line_index].set_3d_properties(z_vals)

    # Plot color order for leg links: (hip, upper leg, lower leg)
    line_index = 4  
    for leg in coords:
        for i in range(3):                
            x_vals = [leg[i][0], leg[i+1][0]]
            y_vals = [leg[i][1], leg[i+1][1]]
            z_vals = [leg[i][2], leg[i+1][2]]
            lines[line_index].set_data(x_vals,y_vals)
            lines[line_index].set_3d_properties(z_vals)
            line_index += 1
          
    fig.canvas.draw()
    fig.canvas.flush_events()
    
    sleep(0.010)