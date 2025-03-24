#!/usr/bin/env python3
"""
Basic script to test robot functionality
"""

from lerobot.common.robot_devices.motors.configs import DynamixelMotorsBusConfig
from lerobot.common.robot_devices.motors.dynamixel import DynamixelMotorsBus
from lerobot.common.robot_devices.robots.configs import KochRobotConfig
from lerobot.common.robot_devices.robots.manipulator import ManipulatorRobot

# Create configuration for the follower arm
follower_config = DynamixelMotorsBusConfig(
    port="/dev/tty.usbmodem58FD0170621",
    motors={
        # name: (index, model)
        "shoulder_pan": (1, "xl430-w250"),
        "shoulder_lift": (2, "xl430-w250"),
        "elbow_flex": (3, "xl330-m288"),
        "wrist_flex": (4, "xl330-m288"),
        "wrist_roll": (5, "xl330-m288"),
        "gripper": (6, "xl330-m288"),
    },
)

# Create the robot configuration
robot_config = KochRobotConfig(
    follower_arms={"main": follower_config},
    leader_arms={},  # Explicitly set to empty dictionary to indicate no leader arms
    cameras={},  # We don't use any camera for now
)

# Create the robot instance
robot = ManipulatorRobot(robot_config)

# Function to initialize and test the robot
def test_robot():
    print("Connecting to the robot...")
    robot.connect()
    print("Robot connected successfully!")
    
    # Add test code here
    
    print("Disconnecting from the robot...")
    robot.disconnect()
    print("Robot disconnected successfully!")

if __name__ == "__main__":
    test_robot()