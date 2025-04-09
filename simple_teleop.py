#!/usr/bin/env python3

import time
import tqdm
from lerobot.common.robot_devices.motors.configs import DynamixelMotorsBusConfig
from lerobot.common.robot_devices.motors.dynamixel import DynamixelMotorsBus, TorqueMode

print("Simple Teleoperation Script for Koch v1.1")
print("==========================================")
print("SAFETY FIRST: This script will connect to your robot but won't move it")
print("until you explicitly allow it.")
print("\nMake sure:")
print("- 5V power supply is connected to the leader arm")
print("- 12V power supply is connected to the follower arm")
print("- USB cables are properly connected")
print("\nPress Enter to connect to the robot (NO MOVEMENT WILL HAPPEN)...")
input()

try:
    # Configure the arms
    print("\nConfiguring leader arm...")
    leader_config = DynamixelMotorsBusConfig(
        port="/dev/tty.usbmodem58FD0171591",
        motors={
            # name: (index, model)
            "shoulder_pan": (1, "xl330-m077"),
            "shoulder_lift": (2, "xl330-m077"),
            "elbow_flex": (3, "xl330-m077"),
            "wrist_flex": (4, "xl330-m077"),
            "wrist_roll": (5, "xl330-m077"),
            "gripper": (6, "xl330-m077"),
        },
    )
    
    print("Configuring follower arm...")
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
    
    # Create instances
    leader_arm = DynamixelMotorsBus(leader_config)
    follower_arm = DynamixelMotorsBus(follower_config)
    
    # Connect to arms - NO MOVEMENT YET
    print("\nConnecting to leader arm...")
    leader_arm.connect()
    print("✅ Leader arm connected!")
    
    print("\nConnecting to follower arm...")
    follower_arm.connect()
    print("✅ Follower arm connected!")
    
    # Get initial positions (read-only, no movement)
    try:
        leader_pos = leader_arm.read("Present_Position")
        follower_pos = follower_arm.read("Present_Position")
        print(f"\nInitial leader positions: {leader_pos}")
        print(f"Initial follower positions: {follower_pos}")
    except Exception as e:
        print(f"Warning: Could not read positions, but connection is ok: {e}")
    
    # ASK before enabling torque
    print("\n=== SAFETY CHECK ===")
    print("To start teleoperation, make sure:")
    print("1. The robot is in a safe position")
    print("2. There are no obstacles in the way")
    print("3. You're ready to supervise the movement")
    print("\nDo you want to enable torque and start teleoperation? (yes/no)")
    
    response = input("> ").strip().lower()
    if response != "yes":
        print("Operation cancelled. No torque will be enabled.")
        # Exit the script without enabling torque
        raise SystemExit("User chose not to proceed")
    
    # Enable torque on follower arm
    print("\nEnabling torque on follower arm...")
    follower_arm.write("Torque_Enable", TorqueMode.ENABLED.value)
    print("✅ Torque enabled!")
    
    # Set profile velocity for smoother movement
    print("\nSetting profile velocity...")
    follower_arm.write("Profile_Velocity", 20)
    print("✅ Profile velocity set!")
    
    print("\nStarting teleoperation for 30 seconds...")
    print("Move the leader arm to control the follower arm")
    print("Press Ctrl+C to stop early")
    
    # Teleoperate for 30 seconds
    seconds = 30
    frequency = 100
    
    for _ in tqdm.tqdm(range(seconds * frequency)):
        # Read positions from leader arm
        leader_pos = leader_arm.read("Present_Position")
        
        # Write positions to follower arm
        follower_arm.write("Goal_Position", leader_pos)
        
        # Short delay to control frequency
        time.sleep(1 / frequency)
    
    print("\n✅ Teleoperation complete!")

except SystemExit as e:
    print(f"\n{e}")
except Exception as e:
    print(f"\n❌ Error: {e}")

finally:
    print("\nCleaning up...")
    try:
        # Safely disable torque on follower arm
        print("Disabling torque on follower arm...")
        follower_arm.write("Torque_Enable", TorqueMode.DISABLED.value)
        print("✅ Torque disabled!")
        
        # Disconnect from arms
        print("Disconnecting from arms...")
        leader_arm.disconnect()
        follower_arm.disconnect()
        print("✅ Disconnected!")
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
    
    print("\nDone! You can now unplug the power supplies.") 