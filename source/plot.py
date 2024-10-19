#!/usr/bin/env python3

"""
    Creates a 3D wire plot of a quadruped body and legs.
    Gamepad controls the quadruped for live rotation and translation updates.
    
    Used to validate body frame, inverse kinematics, and pose input (gaits) prior to applying code to physics simulations or physical system.
"""

import matplotlib.pyplot as plt
from math import pi
from time import sleep

# Local source.
from quadruped.body import Body
from quadruped.gamepad_interface import GamepadInterface
from quadruped.parameters.frame_parameters import FrameParameters
from quadruped.parameters.motion_parameters import MotionParameters


class Plot:
    def __init__(self, frame_parameters: FrameParameters):

        self.body = Body(frame_parameters=frame_parameters)

    def create_plot(self):
        """Create the 3D plot"""

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(projection="3d")

        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_zlabel("Z")

        self.ax.set_xlim([-0.25, 0.25])
        self.ax.set_ylim([0.0, 0.4])
        self.ax.set_zlim([-0.2, 0.2])

        self.ax.view_init(elev=-45, azim=45, roll=45)

        plt.ion()
        plt.show()

    def update_plot(self, motion_parameters: MotionParameters):
        for text in plt.gca().texts:
            text.remove()

        error_state = self.body.set_body_pose_by_transform_inputs(
            phi=motion_parameters.roll,
            theta=motion_parameters.pitch,
            psi=motion_parameters.yaw,
            x=motion_parameters.side_translation,
            y=motion_parameters.height_translation,
            z=motion_parameters.forward_translation,
        )
        if error_state == Body.ErrorState.NONE:

            for line in plt.gca().lines:
                line.remove()

            # Set leg angles to zero degrees to determine zeroed position.
            # a = ((0,0,0), (0,0,0), (0,0,0), (0,0,0))
            # body.set_leg_angles(a)

            coords = self.body.get_leg_coordinates()

            # Construct the body of 4 lines from the first point of each leg (the four corners of the body)
            for i in range(4):
                # For last leg, connect back to first leg point
                if i == 3:
                    ind = -1
                else:
                    ind = i
                x_vals = [coords[ind][0][0], coords[ind + 1][0][0]]
                y_vals = [coords[ind][0][1], coords[ind + 1][0][1]]
                z_vals = [coords[ind][0][2], coords[ind + 1][0][2]]
                self.ax.plot(x_vals, y_vals, z_vals, color="k", marker="o")[0]

            # Plot color order for leg links: (hip, upper leg, lower leg)
            plt_colors = ["r", "c", "b"]
            for leg in coords:
                for i in range(3):
                    x_vals = [leg[i][0], leg[i + 1][0]]
                    y_vals = [leg[i][1], leg[i + 1][1]]
                    z_vals = [leg[i][2], leg[i + 1][2]]
                    self.ax.plot(
                        x_vals, y_vals, z_vals, color=plt_colors[i], marker="o"
                    )[0]
        else:
            # Alert user there is a calculation or bounds error
            self.ax.text(
                0,
                0,
                0,
                error_state.name,
                fontsize=12,
                color="black",
                bbox=dict(facecolor="red", alpha=0.5, edgecolor="red"),
            )

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()


###############################################################################
# Entry
###############################################################################
if __name__ == "__main__":

    motion_parameters_filepath = "./quadruped/parameters/motion_parameters.yaml"
    frame_parameters_filepath = "./quadruped/parameters/frame_parameters.yaml"

    frame_parameters = FrameParameters(frame_parameters_filepath)
    motion_parameters = MotionParameters(motion_parameters_filepath)

    gamepad_interface = GamepadInterface(motion_parameters)
    gamepad_interface.connect_gamepad()

    plot = Plot(frame_parameters)
    plot.create_plot()

    try:        
        
        if gamepad_interface.is_connected():
            """Use gamepad to update motion parameters"""
            while gamepad_interface.is_connected():               
                gamepad_interface.tick()
                motion_parameters = gamepad_interface.get_motion_parameters()
                plot.update_plot(motion_parameters) 
                sleep(0.010)
        else:
            """Manually create motion parameters to generate a demo pose"""
            motion_parameters = MotionParameters(motion_parameters_filepath)
            motion_parameters.height_translation = 0.200
            plot.update_plot(motion_parameters)
            while(True):
                # Wait for user to exit via ctrl-c
                sleep(0.010)
            
    except Exception as e:
        print(str(e))
              
    gamepad_interface.disconnect()
