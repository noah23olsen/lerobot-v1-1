#!/usr/bin/env python3
import os
import sys
import time
from lerobot.common.robot_devices.motors.configs import DynamixelMotorsBusConfig
from lerobot.common.robot_devices.motors.dynamixel import DynamixelMotorsBus, TorqueMode
import numpy as np
from getch import getch

# Configure your robot arm
follower_config = DynamixelMotorsBusConfig(
    port="/dev/tty.usbmodem58FD0170621",
    motors={
        # name: (index, model)
        "shoulder_pan": (1, "xl430-w250"),  # Left/right rotation of base
        "shoulder_lift": (2, "xl430-w250"), # Up/down movement of shoulder
        "elbow_flex": (3, "xl330-m288"),    # Elbow up/down
        "wrist_flex": (4, "xl330-m288"),    # Wrist up/down
        "wrist_roll": (5, "xl330-m288"),    # Wrist rotation
        "gripper": (6, "xl330-m288"),       # Gripper open/close
    },
)

# Movement step sizes
STEP_SIZE = 50

print("\n=== ROBOT INTERACTIVE CONTROL ===\n")

print("This script lets you control the robot with simple commands.")
print("\nCONTROLS:")
print("  w: Move elbow UP")
print("  s: Move elbow DOWN")
print("  a: Rotate shoulder LEFT")
print("  d: Rotate shoulder RIGHT")
print("  r: Read current positions")
print("  q: Exit the program")
print("\nMake sure:")
print("- 12V power supply is connected to the follower arm")
print("- USB cable is connected from follower arm to computer")
print("\nPress Enter when ready...")
input()

# Set up graceful exit
def cleanup(arm):
    print("\nDisabling torque...")
    try:
        arm.write("Torque_Enable", TorqueMode.DISABLED.value)
        print("Disconnecting...")
        arm.disconnect()
        print("Done.")
    except Exception as e:
        print(f"Error during cleanup: {e}")
    sys.exit(0)

try:
    print("\nConnecting to robot...")
    arm = DynamixelMotorsBus(follower_config)
    arm.connect()
    print("✅ Connection successful!")
    
    print("\nEnabling torque...")
    arm.write("Torque_Enable", TorqueMode.ENABLED.value)
    print("✅ Torque enabled")
    
    # Set a moderate velocity
    arm.write("Profile_Velocity", 30)
    
    # Read initial positions
    try:
        positions = arm.read("Present_Position")
        print(f"Current positions: {positions}")
        
        # Extract positions we care about
        shoulder_pan_pos = positions[0]  # For left/right (a/d)
        elbow_flex_pos = positions[2]    # For up/down (w/s)
        
        print(f"Shoulder rotation: {shoulder_pan_pos}")
        print(f"Elbow position: {elbow_flex_pos}")
    except Exception as e:
        print(f"Couldn't read positions, using defaults: {e}")
        shoulder_pan_pos = 2028  # Default from custom_moves.py
        elbow_flex_pos = 3139    # Default from custom_moves.py
    
    print("\nReady for control! Enter commands (w/a/s/d/r/q):")
    
    # Main control loop
    while True:
        # Ask for user input
        cmd = input("> ").strip().lower()
        
        if cmd == 'w':
            # Elbow UP
            elbow_flex_pos += STEP_SIZE
            print(f"Moving elbow UP to: {elbow_flex_pos}")
            arm.write("Goal_Position", elbow_flex_pos, "elbow_flex")
            
        elif cmd == 's':
            # Elbow DOWN
            elbow_flex_pos -= STEP_SIZE
            print(f"Moving elbow DOWN to: {elbow_flex_pos}")
            arm.write("Goal_Position", elbow_flex_pos, "elbow_flex")
            
        elif cmd == 'a':
            # Rotate LEFT (shoulder pan)
            shoulder_pan_pos += STEP_SIZE
            print(f"Rotating shoulder LEFT to: {shoulder_pan_pos}")
            arm.write("Goal_Position", shoulder_pan_pos, "shoulder_pan")
            
        elif cmd == 'd':
            # Rotate RIGHT (shoulder pan)
            shoulder_pan_pos -= STEP_SIZE
            print(f"Rotating shoulder RIGHT to: {shoulder_pan_pos}")
            arm.write("Goal_Position", shoulder_pan_pos, "shoulder_pan")
        
        elif cmd == 'r':
            # Read current positions
            try:
                positions = arm.read("Present_Position")
                print("Current positions:")
                print(f"  Shoulder rotation: {positions[0]}")
                print(f"  Shoulder lift: {positions[1]}")
                print(f"  Elbow: {positions[2]}")
                print(f"  Wrist flex: {positions[3]}")
                print(f"  Wrist roll: {positions[4]}")
                print(f"  Gripper: {positions[5]}")
            except Exception as e:
                print(f"Error reading positions: {e}")
        
        elif cmd == 'q':
            print("Exiting...")
            break
        
        else:
            print("Unknown command. Use w/a/s/d/r/q")

except KeyboardInterrupt:
    print("\nProgram interrupted by user.")
    
except Exception as e:
    print(f"Error: {e}")

finally:
    print("\nCleaning up...")
    print("Disabling torque...")
    try:
        arm.write("Torque_Enable", TorqueMode.DISABLED.value)
        print("Disconnecting...")
        arm.disconnect()
        print("✅ Done.")
    except Exception as e:
        print(f"Error during cleanup: {e}") 