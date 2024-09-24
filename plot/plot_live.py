#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
import matplotlib.animation as animation
from math import pi
from StickFigure import StickFigure

import os
import yaml
from GamepadInterface import GamepadInterface
from time import sleep


motion_parameters_filepath = "./parameters/motion_parameters.yaml"
frame_parameters_filepath = "./parameters/frame_parameters.yaml"       
    
if os.path.exists(motion_parameters_filepath):
    with open(motion_parameters_filepath, 'r') as stream:
        motion_parameters = yaml.safe_load(stream)
else:
    print(f"[Commander] parameter file not found! {motion_parameters_filepath}")

if os.path.exists(frame_parameters_filepath):
    with open(frame_parameters_filepath, 'r') as stream:
        frame_parameters = yaml.safe_load(stream)
else:
    print(f"[Commander] parameter file not found! {frame_parameters_filepath}")



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

# Instantiate spot micro stick figure obeject
sm = StickFigure(x=0,y=0.14,z=0, theta=00*d2r)

# Define absolute position for the legs
l = sm.body_length
w = sm.body_width
l1 = sm.hip_length
l2 = sm.upper_leg_length
l3 = sm.lower_leg_length
desired_p4_points = np.array([ [-l/2,   0,  w/2 + l1],
                               [ l/2 ,  0,  w/2 + l1],
                               [ l/2 ,  0, -w/2 - l1],
                               [-l/2 ,  0, -w/2 - l1] ])

sm.set_absolute_foot_coordinates(desired_p4_points)

# Set a pitch angle
sm.set_body_angles(theta=00*d2r)

# Get leg coordinates
coords = sm.get_leg_coordinates()

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

    roll = motion_inputs.orn[0]
    pitch = motion_inputs.orn[1]
    yaw = motion_inputs.orn[2]

    sm.set_body_angles(phi=roll,theta=pitch,psi=yaw)
    coords = sm.get_leg_coordinates()

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