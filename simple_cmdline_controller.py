import time
from motors import Motors

import argparse

def main_loop(motor_index: int = 0, dir: int = 1, speed: float = 1, debug=False):
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
        debug=debug)
    
    print('Running motor', motor_index, 'forward' if dir > 0 else 'backward', 'at speed', speed)
    if dir > 0:
        motors.dir_motor_forward([motor_index])
    else:
        motors.dir_motor_backward([motor_index])
    motors.set_motor_speed([motor_index], speed)
    motors.start_motor([motor_index])

    print("Starting main loop.")

    try:
        while True:
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
    parser.add_argument(
        "direction", 
        help="Direction of motor spin, 1 or -1",
        type=int)
    parser.add_argument(
        "speed", 
        help="Speed of motor spin, 0 to 1",
        type=float)
    parser.add_argument("--debug", action="store_true")

    cmd_args = parser.parse_args()
    main_loop(cmd_args.motor_index, cmd_args.direction, cmd_args.speed, debug=cmd_args.debug)