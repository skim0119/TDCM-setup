import time
from motors import Motors
# from keyboard_control import MyListener

import argparse
import sys

def main_loop(motor_index: int = 0, dir: int = 1, speed: float = 1):
    PUL = [17, 25, 22] 
    DIR = [27, 24, 23] 
    MOTOR_ORIENTATION = [True, True, False]

    motors = Motors(
        PUL, 
        DIR, 
        MOTOR_ORIENTATION, 
        steps_per_rev=1600, 
        max_rpm=30, 
        pulse_width=10 * 1e-6,
        debug=False)
    
    print('Running motor', motor_index, 'forward' if dir > 0 else 'backward', 'at speed', speed)
    if dir > 0:
        motors.dir_motor_forward([motor_index])
    else:
        motors.dir_motor_backward([motor_index])
    motors.set_motor_speed([motor_index], speed)
    motors.start_motor([motor_index])

    # state = {"direction": 1, "speed": 1}
    # listener = MyListener(state)
    # listener.start()

    print("Starting main loop.")

    try:
        while True:
            # if state["direction"] > 0:
            #     motors.dir_motor_forward()
            # else:
            #     motors.dir_motor_backward()
            # motors.set_motor_speed([2], state["speed"])
            motors.update([0, 1, 2])
    except KeyboardInterrupt:
        print("\nMain loop interrupted by Ctrl+C.")
    finally:
        motors.stop_motor([0, 1, 2])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "motor_index", 
        help="Index of motor to spin, corresponding to list index of pins",
        type=int)

    cmd_args = parser.parse_args()
    print(cmd_args.motor_index)

    cmd_args = [float(a) for a in sys.argv[1:]]
    cmd_args[0] = int(cmd_args[0])
    cmd_args[1] = int(cmd_args[1])
    n = len(cmd_args)
    if n == 0:
        main_loop()
    elif n == 3:
        main_loop(*cmd_args)
    else:
        print("invalid args: ", cmd_args)
        main_loop()