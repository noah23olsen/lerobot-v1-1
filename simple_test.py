#!/usr/bin/env python3

from lerobot.common.robot_devices.motors.configs import DynamixelMotorsBusConfig
from lerobot.common.robot_devices.motors.dynamixel import DynamixelMotorsBus, TorqueMode
import time

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

print("\n--- SIMPLE ROBOT TEST ---\n")

print("Step 1: Make sure your robot is properly connected:")
print("- 12V power supply connected to the follower arm")
print("- USB cable connected from follower arm to computer")
print("\nPress Enter when ready...")
input()

try:
    print("\nConnecting to robot...")
    arm = DynamixelMotorsBus(follower_config)
    arm.connect()
    print("✅ Connection successful!")
    
    print("\nTrying to enable torque...")
    arm.write("Torque_Enable", TorqueMode.ENABLED.value)
    print("✅ Torque enabled!")
    
    # Try to move just the gripper
    print("\nTrying to move the gripper...")
    try:
        # Get current position of gripper
        gripper_pos = arm.read("Present_Position", "gripper")
        print(f"Current gripper position: {gripper_pos}")
        
        # Move gripper +100 steps
        print(f"Moving gripper to {gripper_pos + 100}...")
        arm.write("Goal_Position", gripper_pos + 100, "gripper")
        time.sleep(2)
        
        # Move gripper -100 steps
        print(f"Moving gripper to {gripper_pos - 100}...")
        arm.write("Goal_Position", gripper_pos - 100, "gripper")
        time.sleep(2)
        
        # Move back to original position
        print(f"Moving gripper back to {gripper_pos}...")
        arm.write("Goal_Position", gripper_pos, "gripper")
        time.sleep(2)
        
        print("✅ Gripper movement successful!")
    except Exception as e:
        print(f"❌ Failed to move gripper: {e}")
    
    # Try to read all positions
    print("\nTrying to read positions of all joints...")
    try:
        positions = arm.read("Present_Position")
        print(f"All joint positions: {positions}")
        print("✅ Position reading successful!")
    except Exception as e:
        print(f"❌ Failed to read positions: {e}")

except Exception as e:
    print(f"❌ Error: {e}")

finally:
    try:
        print("\nDisabling torque...")
        arm.write("Torque_Enable", TorqueMode.DISABLED.value)
        print("✅ Torque disabled!")
        
        print("\nDisconnecting...")
        arm.disconnect()
        print("✅ Robot disconnected!")
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

print("\n--- TEST COMPLETE ---") 