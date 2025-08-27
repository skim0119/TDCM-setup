import time
import keyboard
import threading
from motors import Motors
import numpy as np
# from keyboard_control import MyListener
import sys
import pygame
from pygame import joystick
pygame.init()
pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
joy = pygame.joystick.Joystick(0)
joy.init()

def main_loop(motors,motor_index: int = 0, dir: int = 1, speed: float = 1):
    

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
    Action = True
    start_step = motors.num_of_steps[motor_index]
    duration = 500

    try:
        while Action:
            # if state["direction"] > 0:
            #     motors.dir_motor_forward()
            # else:
            #     motors.dir_motor_backward()
            # motors.set_motor_speed([2], state["speed"])
            current_step = motors.num_of_steps[motor_index]
            elapsed = current_step - start_step
            motors.update([0, 1, 2])
            if abs(elapsed) >= duration: Action = False
    except KeyboardInterrupt:
        print("\nMain loop interrupted by Ctrl+C.")
    finally:
        motors.stop_motor([0, 1, 2])
        print(motors.motor_direction)
        print(motors.num_of_steps)

def home_arm(motors):
    print("Moving the Arm to Home Position...")
    
    for motor_index in range(len(motors._PUL_devices)):
        print(motor_index)
        if motors.num_of_steps[motor_index] > 0:
             motors.dir_motor_backward([motor_index])
        else:
             motors.dir_motor_forward([motor_index])
        motors.set_motor_speed([motor_index], 1)
        motors.start_motor([motor_index])
        #start_step = motors.num_of_steps.copy()
        #target_steps = list(np.subtract([0,0,0],start_step))
        target = [0,0,0]
        Action = True

        #print("motor_directions",motors.motor_direction)
        #print("motor_running",motors._motor_running)
    try:
        while Action:
            
            
            
            current_step = motors.num_of_steps.copy()
            gap_step = [abs(a - b) for a,b in zip(target,current_step)]
            motors.update([0, 1, 2])
            
            print(current_step,"|motor_running",motors._motor_running,"|motor_directions",motors.motor_direction,"|target_step",target)
            
            for motor_index in range(len(motors._PUL_devices)):
                if gap_step[motor_index] <= 0:
                    motors.stop_motor([motor_index])

            if np.sum(motors._motor_running) == 0:
                Action = False
            
    except KeyboardInterrupt:
        print("\nMain loop interrupted by Ctrl+C.")

    finally:
        motors.stop_motor([0, 1, 2])
        print(motors.motor_direction)
        print(motors.num_of_steps)

    
    print("Arm has been Homed")

def listen_for_home_command(motors):
    print("Listening for command...") 
    input_buffer = ""
    while True:

        cmd = input()
        if cmd.strip().lower() == "home the robot":
            home_arm(motors)
            
def button_reaction(mode: int):
    if mode == 0: direction = -1  # Standard mode
    elif mode == 1: direction = 1 # Left_button is pressed
    
    A_pressed = joy.get_button(0)
    B_pressed = joy.get_button(1)
    X_pressed = joy.get_button(2)
    if joy.get_button(3):
        Y_button_case(mode)
    if A_pressed: button = 2
    elif B_pressed: button = 0
    elif X_pressed: button = 1

    if A_pressed or B_pressed or X_pressed: 
        args = [motors,button,direction,1]
        main_loop(*args)

    return 0

def Y_button_case(mode):
    if mode == 0:
        # Show Current num_of_step
        print("Current num_of_step:",motors.num_of_steps)
        return 0
    elif mode == 1:
        # Calibrate Step Mannully by pressing Y
        motors.num_of_steps = [0,0,0]
        print("Your step record has been calibrated! Current num_of_step:",motors.num_of_steps)
    

if __name__ == "__main__":     
    print("Start Program")  


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
        
    listener_thread = threading.Thread(target=listen_for_home_command, args = (motors,),daemon = True)
    
    listener_thread.start()

    
    try :

        while True:
            pygame.event.pump()
            button_to_motor = {0:0,1:1,2:2}
            ALLOWED_BUTTON = {0,1,2}
            
            for event in pygame.event.get():
                if event.type  == pygame.JOYBUTTONDOWN:
                    if joy.get_button(4):
                        button_reaction(1)
                    else:
                        button_reaction(0)
                if event.type == pygame.JOYBUTTONUP:
                    pass
    
            
    except KeyboardInterrupt:
        print("Main loop interrupted")
    finally:
        pass
        
    
