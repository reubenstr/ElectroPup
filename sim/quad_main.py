'''
    ROS2 Wrapper for quad_main
'''

from time import sleep
import rclpy
from rclpy.node import Node
import numpy as np
import copy
import yaml
import io
from os import path, read

from rclpy.executors import SingleThreadedExecutor
from sensor_msgs.msg import Joy
from quad_interfaces.msg import JointAngles
from rclpy.logging import LoggingSeverity
from rclpy.parameter import Parameter

from src.quad_commander import QuadCommander
from src.joystick_interpreter import JoystickInterpreter
from src.motion_inputs import MotionInputs

class JoystickSubscriber(Node):
    def __init__(self, motion_parameters):
        super().__init__('joy_subscriber_node')
        self.subscription = self.create_subscription(
            Joy, 'joy', self.listener_callback, 10)
        self.joystick_interpreter = JoystickInterpreter(motion_parameters)
        self.motion_inputs = MotionInputs()

    def listener_callback(self, msg):
        axes = msg.axes
        buttons = msg.buttons
        self.motion_inputs = self.joystick_interpreter.get_motion_inputs(
            axes, buttons)

    def get_motion_parameters(self):
        return copy.deepcopy(self.motion_inputs)


class JointAnglesPublisher(Node):
    def __init__(self):
        super().__init__('joint_angles_publisher_node')
        self.publisher_ = self.create_publisher(JointAngles, 'joint_angles', 10)
        timer_period_ms = 0.020
        self.timer = self.create_timer(timer_period_ms, self.timer_callback)       
        self.joint_angles = np.empty([12])
        self.joint_angles_linked_leg = np.empty([12])
           
    def set_joint_angles(self, joint_angles):
        self.joint_angles = joint_angles

    def set_joint_angles_linked_leg(self, joint_angles_linked_leg):
        self.joint_angles_linked_leg = joint_angles_linked_leg

    def timer_callback(self):
        msg = JointAngles()   
        # TODO: remove the loop
        for i in range(12):
            msg.joint_angles[i] = self.joint_angles[i]
            msg.joint_angles_linked_leg[i] = self.joint_angles_linked_leg[i]
        self.publisher_.publish(msg)  

def main(args=None):
    rclpy.init(args=args)
    rclpy.logging._root_logger.log("QUAD STARTED", LoggingSeverity.INFO)

    joint_angles_publisher_node = JointAnglesPublisher()
    
    joint_angles_publisher_node.declare_parameters(
        namespace='',
        parameters=[      
            ('motion_parameters_path', None),   
            ('frame_parameters_path', None),
            ('linked_leg_parameters_path', None)])
   
    motion_parameters_path = joint_angles_publisher_node.get_parameter(
        'motion_parameters_path').get_parameter_value().string_value
    frame_parameters_path = joint_angles_publisher_node.get_parameter(
        'frame_parameters_path').get_parameter_value().string_value
    linked_leg_parameters_path = joint_angles_publisher_node.get_parameter(
        'linked_leg_parameters_path').get_parameter_value().string_value       
    
    rclpy.logging._root_logger.log(
        "motion_parameters_path: " + motion_parameters_path, LoggingSeverity.INFO)
    rclpy.logging._root_logger.log(
        "frame_parameters_path: " + frame_parameters_path, LoggingSeverity.INFO)
    rclpy.logging._root_logger.log(
        "linked_leg_parameters_path: " + linked_leg_parameters_path, LoggingSeverity.INFO)
  
    # TODO: catch exception if file not found
    if path.exists(motion_parameters_path):
        with open(motion_parameters_path, 'r') as stream:
            motion_parameters = yaml.safe_load(stream)

    if path.exists(frame_parameters_path):
        with open(frame_parameters_path, 'r') as stream:
            frame_parameters = yaml.safe_load(stream)

    if path.exists(linked_leg_parameters_path):
        with open(linked_leg_parameters_path, 'r') as stream:
            linked_leg_parameters = yaml.safe_load(stream)

    joystick_subscriber = JoystickSubscriber(motion_parameters)
    
    quad_commander = QuadCommander(motion_parameters, frame_parameters, linked_leg_parameters)

    executor = SingleThreadedExecutor()
    executor.add_node(joint_angles_publisher_node)
    executor.add_node(joystick_subscriber)
    
    while rclpy.ok():
        motion_inputs = joystick_subscriber.get_motion_parameters()
          
        joint_angles, joint_angles_linked_leg = quad_commander.tick(
            motion_inputs)
       
        joint_angles_publisher_node.set_joint_angles(joint_angles)
        joint_angles_publisher_node.set_joint_angles_linked_leg(joint_angles_linked_leg)
      
        executor.spin_once()

    executor.shutdown()
    joint_angles_publisher_node.destroy_node()
    joystick_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
