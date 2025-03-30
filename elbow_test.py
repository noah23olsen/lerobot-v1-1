#!/usr/bin/env python3

from lerobot.common.robot_devices.motors.configs import DynamixelMotorsBusConfig
from lerobot.common.robot_devices.motors.dynamixel import DynamixelMotorsBus, TorqueMode
import time
import numpy as np

# Configure your robot arm
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

print("\n=== ELBOW JOINT DIAGNOSTIC TEST ===\n")

print("This script will specifically test the elbow_flex joint (motor #3)")
print("We'll try to examine the issue where the elbow joint doesn't move.")
print("\nMake sure:")
print("- 12V power supply is connected to the follower arm")
print("- USB cable is connected from follower arm to computer")
print("\nPress Enter when ready...")
input()

try:
    print("\nConnecting to robot...")
    arm = DynamixelMotorsBus(follower_config)
    arm.connect()
    print("✅ Connection successful!")
    
    print("\nChecking if we can read from all motors...")
    try:
        all_positions = arm.read("Present_Position")
        print(f"All positions: {all_positions}")
        print("✅ Successfully read from all motors")
        
        # Check specifically the elbow value
        elbow_position = all_positions[2]  # Index 2 corresponds to elbow_flex (3rd motor)
        print(f"Current elbow position: {elbow_position}")
    except Exception as e:
        print(f"❌ Failed to read positions: {e}")
        print("Trying to continue anyway...")
        # Set a default position if we can't read
        all_positions = np.array([2028, 1609, 3139, 3148, 1009, 2507])
        elbow_position = all_positions[2]
    
    print("\nEnabling torque on all motors...")
    arm.write("Torque_Enable", TorqueMode.ENABLED.value)
    print("✅ Torque enabled")
    
    print("\nSetting a slower profile velocity for precision...")
    arm.write("Profile_Velocity", 15)
    print("✅ Profile velocity set")
    
    # Test 1: Try moving just the elbow joint
    print("\n--- TEST 1: Moving ONLY the elbow joint ---")
    print("Testing with large movements (+500 steps)")
    
    try:
        print(f"Current elbow position: {elbow_position}")
        
        # Move elbow +500 steps (large movement)
        new_position = elbow_position + 500
        print(f"Moving elbow to {new_position}...")
        arm.write("Goal_Position", new_position, "elbow_flex")
        time.sleep(5)  # Longer wait to ensure it has time to move
        
        # Read the new position
        try:
            current = arm.read("Present_Position", "elbow_flex")
            print(f"Elbow position after move: {current}")
            if abs(current - new_position) < 50:
                print("✅ Elbow moved successfully!")
            else:
                print("❌ Elbow did not reach target position")
        except Exception as e:
            print(f"❌ Failed to read elbow position: {e}")
        
        # Move elbow -1000 steps (large movement in opposite direction)
        new_position = elbow_position - 500
        print(f"Moving elbow to {new_position}...")
        arm.write("Goal_Position", new_position, "elbow_flex")
        time.sleep(5)  # Longer wait to ensure it has time to move
        
        # Read the new position
        try:
            current = arm.read("Present_Position", "elbow_flex")
            print(f"Elbow position after move: {current}")
            if abs(current - new_position) < 50:
                print("✅ Elbow moved successfully!")
            else:
                print("❌ Elbow did not reach target position")
        except Exception as e:
            print(f"❌ Failed to read elbow position: {e}")
        
        # Move back to original position
        print(f"Moving elbow back to {elbow_position}...")
        arm.write("Goal_Position", elbow_position, "elbow_flex")
        time.sleep(3)
    except Exception as e:
        print(f"❌ Error during elbow test: {e}")
    
    # Test 2: Check if we can control via status LEDs
    print("\n--- TEST 2: Testing LED control for elbow motor ---")
    print("If this works but movement doesn't, it suggests a mechanical or power issue")
    
    try:
        # Turn LED on
        print("Turning elbow motor LED ON...")
        arm.write("LED", 1, "elbow_flex")
        time.sleep(2)
        
        # Turn LED off
        print("Turning elbow motor LED OFF...")
        arm.write("LED", 0, "elbow_flex")
        time.sleep(2)
        
        print("✅ LED control worked")
    except Exception as e:
        print(f"❌ Failed to control LED: {e}")
    
    # Test 3: Check if motor has torque
    print("\n--- TEST 3: Testing torque settings ---")
    
    try:
        # Check current torque enable
        torque = arm.read("Torque_Enable", "elbow_flex")
        print(f"Current torque setting: {torque}")
        
        # Try setting specific operating mode for elbow
        print("Setting Position Control Mode for elbow...")
        
        # Disable torque first (required to change operating mode)
        arm.write("Torque_Enable", TorqueMode.DISABLED.value, "elbow_flex")
        time.sleep(1)
        
        # Set operation mode to position control
        arm.write("Operating_Mode", 3, "elbow_flex")
        time.sleep(1)
        
        # Re-enable torque
        arm.write("Torque_Enable", TorqueMode.ENABLED.value, "elbow_flex")
        time.sleep(1)
        
        # Check if torque is enabled
        torque = arm.read("Torque_Enable", "elbow_flex")
        print(f"Torque setting after change: {torque}")
        
        # Try moving again with a very large movement
        current = arm.read("Present_Position", "elbow_flex")
        print(f"Current elbow position: {current}")
        
        # Move +1000 steps
        new_position = current + 1000
        print(f"Moving elbow to {new_position} with high torque...")
        arm.write("Goal_Position", new_position, "elbow_flex")
        time.sleep(5)
        
        # Read the new position
        try:
            after = arm.read("Present_Position", "elbow_flex")
            print(f"Elbow position after move: {after}")
            if abs(after - new_position) < 50:
                print("✅ Elbow moved successfully with high torque!")
            else:
                print("❌ Elbow still did not reach target position")
        except Exception as e:
            print(f"❌ Failed to read elbow position: {e}")
    except Exception as e:
        print(f"❌ Error during torque test: {e}")

except Exception as e:
    print(f"❌ Error: {e}")

finally:
    try:
        print("\nCleaning up...")
        print("Disabling torque...")
        arm.write("Torque_Enable", TorqueMode.DISABLED.value)
        
        print("Disconnecting...")
        arm.disconnect()
        print("✅ Done.")
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

print("\n=== DIAGNOSTIC COMPLETE ===")
print("\nBased on the test results, this could indicate:")
print("1. Mechanical issue - motor might be seized or cables pinched")
print("2. Power issue - make sure the 12V source is connected")
print("3. Wiring issue - check connections between motors")
print("4. Motor failure - the motor itself might be broken")
print("\nCheck all wiring and connections first, then try again.") 