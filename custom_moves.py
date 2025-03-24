#!/usr/bin/env python3

from lerobot.common.robot_devices.motors.configs import DynamixelMotorsBusConfig
from lerobot.common.robot_devices.motors.dynamixel import DynamixelMotorsBus, TorqueMode
import time
import numpy as np

# Configure your robot arm
follower_config = DynamixelMotorsBusConfig(
    port="/dev/tty.usbmodem58FD0170621",  # Replace with your port if different
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

# CUSTOMIZE THESE VALUES TO CREATE YOUR OWN MOVEMENTS
# --------------------------------------------------

# Define custom poses as offsets from the base position
# Format: [shoulder_pan, shoulder_lift, elbow_flex, wrist_flex, wrist_roll, gripper]
POSES = {
    "home": [0, 0, 0, 0, 0, 0],  # No change from current position
    "uncollapse_1": [0, 100, 0, 0, 0, 0],  # First step to getting up - lift shoulder
    "uncollapse_2": [0, 200, -50, 0, 0, 0],  # Second step - more lift, start straightening elbow
    "uncollapse_3": [0, 300, -150, 0, 0, 0],  # Final uncollapse - full lift and straighten
    "tall": [0, 400, -250, 0, 0, 0],  # MUCH taller stance
    "wave_left": [150, 400, -250, 0, 0, 0],  # Wave to the left
    "wave_right": [-150, 400, -250, 0, 0, 0],  # Wave to the right
    "extend": [0, 250, 150, -100, 0, 0],  # Extended forward
    "dramatic": [100, 450, -300, -80, 150, 100],  # Dramatic pose
    "point_up": [0, 500, -350, 0, 0, 0],  # Point up
    "gripper_open": [0, 0, 0, 0, 0, 150],  # Open gripper
    "gripper_closed": [0, 0, 0, 0, 0, -150],  # Close gripper
    "wrist_spin": [0, 300, -150, 0, 200, 0],  # Wrist rotation
    # Add your own poses here!
}

# Define sequences using the poses above
# Each sequence is a list of (pose_name, duration_in_seconds) tuples
SEQUENCES = {
    "uncollapse": [
        ("uncollapse_1", 3),
        ("uncollapse_2", 3),
        ("uncollapse_3", 3),
        ("tall", 3),
        ("home", 3),
    ],
    "wave": [
        ("uncollapse_3", 3),
        ("tall", 2),
        ("wave_left", 2),
        ("wave_right", 2),
        ("wave_left", 2),
        ("wave_right", 2),
        ("tall", 2),
        ("uncollapse_1", 3),
        ("home", 3),
    ],
    "grab_demo": [
        ("uncollapse_3", 3),
        ("extend", 3),
        ("gripper_open", 2),
        ("gripper_closed", 2),
        ("uncollapse_2", 3),
        ("uncollapse_1", 3),
        ("home", 3),
    ],
    "dramatic_pose": [
        ("uncollapse_3", 3),
        ("tall", 3),
        ("dramatic", 4),
        ("tall", 3),
        ("uncollapse_2", 3),
        ("uncollapse_1", 3),
        ("home", 3),
    ],
    "all_joints": [
        ("uncollapse_1", 3),
        ("uncollapse_2", 3),
        ("uncollapse_3", 3),
        ("tall", 3),
        ("wave_left", 3),
        ("wave_right", 3),
        ("point_up", 3),
        ("tall", 3),
        ("wrist_spin", 3),
        ("tall", 3),
        ("extend", 3),
        ("gripper_open", 2),
        ("gripper_closed", 2),
        ("gripper_open", 2),
        ("tall", 3),
        ("dramatic", 4),
        ("tall", 3),
        ("uncollapse_3", 3),
        ("uncollapse_2", 3),
        ("uncollapse_1", 3),
        ("home", 3),
    ],
    "dance": [
        ("uncollapse_3", 3),
        ("tall", 2),
        ("wave_left", 1.5),
        ("wave_right", 1.5),
        ("point_up", 2),
        ("wrist_spin", 2),
        ("dramatic", 3),
        ("tall", 2),
        ("home", 3),
    ],
    # Add your own sequences here!
}

# CHOOSE WHICH SEQUENCE TO RUN
SEQUENCE_TO_RUN = "dance"  # Change to any sequence name from SEQUENCES

# Movement speed (lower = slower, higher = faster)
VELOCITY_PROFILE = 15  # Slower for safety with larger movements

# --------------------------------------------------
# EXECUTION CODE BELOW - less need to modify this
# --------------------------------------------------

try:
    print("Connecting to robot...")
    arm = DynamixelMotorsBus(follower_config)
    arm.connect()
    
    print("Enabling torque...")
    arm.write("Torque_Enable", TorqueMode.ENABLED.value)
    
    # READ THE CURRENT POSITION FIRST
    print("Reading current position...")
    BASE_POSITION = arm.read("Present_Position")
    print(f"Current position: {BASE_POSITION}")
    
    # Set movement speed
    print(f"Setting profile velocity to {VELOCITY_PROFILE}...")
    arm.write("Profile_Velocity", VELOCITY_PROFILE)
    
    def calculate_position(pose_name):
        """Calculate absolute position from pose offset"""
        if pose_name not in POSES:
            print(f"Warning: Pose '{pose_name}' not found. Using home position.")
            return BASE_POSITION.copy()
        
        position = BASE_POSITION.copy()
        for i in range(6):
            position[i] += POSES[pose_name][i]
        return position
    
    # Ensure we start from home
    print("Moving to home position...")
    arm.write("Goal_Position", BASE_POSITION)
    time.sleep(2)
    
    # Check if selected sequence exists
    if SEQUENCE_TO_RUN not in SEQUENCES:
        print(f"Error: Sequence '{SEQUENCE_TO_RUN}' not found!")
        print(f"Available sequences: {list(SEQUENCES.keys())}")
    else:
        # Execute the selected sequence
        sequence = SEQUENCES[SEQUENCE_TO_RUN]
        print(f"\n=== EXECUTING SEQUENCE: {SEQUENCE_TO_RUN} ===")
        
        for i, (pose_name, duration) in enumerate(sequence):
            print(f"Step {i+1}/{len(sequence)}: Moving to '{pose_name}' pose...")
            position = calculate_position(pose_name)
            arm.write("Goal_Position", position)
            time.sleep(duration)
        
        print("Sequence complete!")

except Exception as e:
    print(f"Error: {e}")

finally:
    try:
        # Reset velocity and ensure we're back home
        print("\nResetting profile velocity...")
        arm.write("Profile_Velocity", 0)
        
        print("Moving to home position...")
        arm.write("Goal_Position", BASE_POSITION)
        time.sleep(2)
        
        print("Disabling torque...")
        arm.write("Torque_Enable", TorqueMode.DISABLED.value)
        
        print("Disconnecting...")
        arm.disconnect()
        print("Done.")
    except Exception as e:
        print(f"Error during cleanup: {e}") 