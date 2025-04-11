from lerobot.common.robot_devices.motors.configs import DynamixelMotorsBusConfig
from lerobot.common.robot_devices.motors.dynamixel import DynamixelMotorsBus, TorqueMode
from lerobot.common.robot_devices.robots.configs import KochRobotConfig
from lerobot.common.robot_devices.robots.manipulator import ManipulatorRobot
import tqdm
import time

print("Simple Koch Robot Control")
print("========================")

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

try:
    # Create instances
    leader_arm = DynamixelMotorsBus(leader_config)
    follower_arm = DynamixelMotorsBus(follower_config)
    
    # Create robot config
    robot_config = KochRobotConfig(
        leader_arms={"main": leader_config},
        follower_arms={"main": follower_config},
        cameras={},  # We don't use any camera for now
    )
    
    # Create robot
    robot = ManipulatorRobot(robot_config)
    
    # Prompt to connect
    input("Press Enter to connect the robot...")
    robot.connect()
    print("Robot connected!")
    
    # Prompt to teleoperate
    input("Press Enter to start teleoperation for 30 seconds...")
    
    # Teleoperate for 30 seconds
    seconds = 30
    frequency = 200
    print(f"Teleoperating for {seconds} seconds...")
    
    for _ in tqdm.tqdm(range(seconds*frequency)):
        leader_pos = robot.leader_arms["main"].read("Present_Position")
        robot.follower_arms["main"].write("Goal_Position", leader_pos)
        time.sleep(1/frequency)
    
    print("Teleoperation complete!")

except Exception as e:
    print(f"Error: {e}")

finally:
    # Clean up
    print("Cleaning up...")
    try:
        # Disable torque
        for name in robot.follower_arms:
            robot.follower_arms[name].write("Torque_Enable", TorqueMode.DISABLED.value)
        
        # Disconnect
        robot.disconnect()
        print("Robot disconnected safely!")
    except Exception as e:
        print(f"Error during cleanup: {e}")