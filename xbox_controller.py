import time
from motors import Motors
# from keyboard_control import MyListener
import sys
import pygame
from pygame import joystick
pygame.init()
pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
joy = pygame.joystick.Joystick(0)
joy.init()
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
    Action = True
    start_time = time.time()
    duration = 0.5
    try:
        while Action:
            # if state["direction"] > 0:
            #     motors.dir_motor_forward()
            # else:
            #     motors.dir_motor_backward()
            # motors.set_motor_speed([2], state["speed"])
            current_time = time.time()
            elapsed = current_time - start_time
            motors.update([0, 1, 2])
            if elapsed > Action: Action = False
    except KeyboardInterrupt:
        print("\nMain loop interrupted by Ctrl+C.")
    finally:
        motors.stop_motor([0, 1, 2])


if __name__ == "__main__":       
    try :
        while True:
            pygame.event.pump()
            button_to_motor = {0:0,1:1,2:2}
            ALLOWED_BUTTON = {0,1,2}
            for event in pygame.event.get():
                if event.type  == pygame.JOYBUTTONDOWN:
                    if joy.get_button(4):
                        print(joy.get_button(4))
                        A_pressed = joy.get_button(0)
                        B_pressed = joy.get_button(1)
                        X_pressed = joy.get_button(2)
                        if A_pressed: button = 2
                        elif B_pressed: button = 0
                        elif X_pressed: button = 1
                    
                        if A_pressed or B_pressed or X_pressed: 
                            args = [button,1,1]
                            main_loop(*args)
                        else:
                            pass
                    else:
                        print(joy.get_button(4))
                        A_pressed = joy.get_button(0)
                        B_pressed = joy.get_button(1)
                        X_pressed = joy.get_button(2)
                        if A_pressed: button = 2
                        elif B_pressed: button = 0
                        elif X_pressed: button = 1
                    
                        if A_pressed or B_pressed or X_pressed: 
                            args = [button,-1,1]
                            main_loop(*args)
                        else:
                            pass
                if event.type == pygame.JOYBUTTONUP:
                    pass
                #if event.type == pygame.JOYAXISMOTION:
                 #   args = [event.button,1,1*event.value]
                  #  main_loop(*args)
    except KeyboardInterrupt:
        print("Main loop interrupted")
    finally:
        pass
