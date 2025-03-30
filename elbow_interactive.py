#!/usr/bin/env python3

from lerobot.common.robot_devices.motors.configs import DynamixelMotorsBusConfig
from lerobot.common.robot_devices.motors.dynamixel import DynamixelMotorsBus, TorqueMode
import time
import sys

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

# Set the step size for movements - can be adjusted
STEP_SIZE = 100  # Increased for faster movement

# Starting positions - will be updated when we move
shoulder_pan_pos = 2000  # Middle position for shoulder
elbow_flex_pos = 3300    # Middle position for elbow

print("\n=== ROBOT DIRECT CONTROL - FULL RANGE ===\n")

print("This script directly controls the robot with NO SAFETY LIMITS:")
print("\nCONTROLS:")
print("  w: Move elbow UP by 100 steps")
print("  s: Move elbow DOWN by 100 steps")
print("  a: Rotate shoulder LEFT by 100 steps")
print("  d: Rotate shoulder RIGHT by 100 steps")
print("  +: Increase step size by 50")
print("  -: Decrease step size by 50")
print("  h: Go to home position")
print("  r: Try to read current positions")
print("  v: Check motor voltage (helps diagnose power issues)")
print("  q: Exit the program")
print("\nVOLTAGE TROUBLESHOOTING:")
print("- If motors aren't moving, check that the 12V power supply is firmly connected")
print("- Make sure the power supply is plugged into a working outlet")
print("- For best performance, avoid using the robot on a low battery or through USB hubs")
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
    
    print("\nEnabling torque...")
    arm.write("Torque_Enable", TorqueMode.ENABLED.value)
    print("✅ Torque enabled")
    
    # Set a higher velocity for faster movements
    arm.write("Profile_Velocity", 50)
    
    # Try to read initial positions
    try:
        positions = arm.read("Present_Position")
        print(f"Current positions: {positions}")
        shoulder_pan_pos = positions[0]
        elbow_flex_pos = positions[2]
    except Exception as e:
        print(f"Could not read positions: {e}")
        print("Using default positions instead")
    
    print(f"Starting shoulder position: {shoulder_pan_pos}")
    print(f"Starting elbow position: {elbow_flex_pos}")
    print(f"Current step size: {STEP_SIZE}")
    
    print("\nReady for control! Enter commands (w/a/s/d/+/-/h/r/v/q):")
    
    # Main control loop
    while True:
        cmd = input("> ").strip().lower()
        
        if cmd == 'w':
            # Elbow UP
            elbow_flex_pos += STEP_SIZE
            print(f"Moving elbow UP to: {elbow_flex_pos}")
            try:
                arm.write("Goal_Position", elbow_flex_pos, "elbow_flex")
                time.sleep(0.2)  # Short pause for movement
            except Exception as e:
                print(f"Error moving elbow: {e}")
            
        elif cmd == 's':
            # Elbow DOWN
            elbow_flex_pos -= STEP_SIZE
            print(f"Moving elbow DOWN to: {elbow_flex_pos}")
            try:
                arm.write("Goal_Position", elbow_flex_pos, "elbow_flex")
                time.sleep(0.2)  # Short pause for movement
            except Exception as e:
                print(f"Error moving elbow: {e}")
            
        elif cmd == 'a':
            # Rotate LEFT
            shoulder_pan_pos += STEP_SIZE
            print(f"Rotating shoulder LEFT to: {shoulder_pan_pos}")
            try:
                arm.write("Goal_Position", shoulder_pan_pos, "shoulder_pan")
                time.sleep(0.2)  # Short pause for movement
            except Exception as e:
                print(f"Error rotating shoulder: {e}")
            
        elif cmd == 'd':
            # Rotate RIGHT
            shoulder_pan_pos -= STEP_SIZE
            print(f"Rotating shoulder RIGHT to: {shoulder_pan_pos}")
            try:
                arm.write("Goal_Position", shoulder_pan_pos, "shoulder_pan")
                time.sleep(0.2)  # Short pause for movement
            except Exception as e:
                print(f"Error rotating shoulder: {e}")
        
        elif cmd == '+':
            # Increase step size
            STEP_SIZE += 50
            print(f"Step size increased to: {STEP_SIZE}")
            
        elif cmd == '-':
            # Decrease step size
            if STEP_SIZE > 50:
                STEP_SIZE -= 50
                print(f"Step size decreased to: {STEP_SIZE}")
            else:
                print("Step size already at minimum (50)")
                
        elif cmd == 'h':
            # Go to home position
            print("Moving to home position...")
            shoulder_pan_pos = 2000  # Center position
            elbow_flex_pos = 3200    # Middle position
            try:
                # Move shoulder first
                arm.write("Goal_Position", shoulder_pan_pos, "shoulder_pan")
                time.sleep(0.5)
                # Then move elbow
                arm.write("Goal_Position", elbow_flex_pos, "elbow_flex")
                time.sleep(0.5)
                print("✅ Home position reached")
            except Exception as e:
                print(f"Error moving to home: {e}")
        
        elif cmd == 'r':
            # Try to read positions
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
        
        elif cmd == 'v':
            # Try to read voltage
            try:
                # Read present voltage from all motors (typically register 144)
                voltage = arm.read("Present_Input_Voltage")
                print(f"Motor voltages (in 0.1V units): {voltage}")
                print(f"Elbow motor voltage: {voltage[2]/10.0}V")
                
                if any(v < 110 for v in voltage):  # Less than 11V
                    print("⚠️ Warning: LOW VOLTAGE detected! Some motors may not function properly.")
                    print("Check that the 12V power supply is firmly connected and working.")
                else:
                    print("✅ Voltage levels look good!")
            except Exception as e:
                print(f"Error reading voltage: {e}")
                print("Try checking physical connections and power source.")
        
        elif cmd == 'q':
            print("Exiting...")
            break
        
        else:
            print("Unknown command. Use w/a/s/d/+/-/h/r/v/q")

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