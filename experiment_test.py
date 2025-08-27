from arm_system import Arm_System
from motor_advance import Spirob_Motors
from vision_capture import Vision_System
import time
import numpy as np
import cv2
# Initiling the System

PUL = [17, 25, 22] 
DIR = [27, 24, 23] 
MOTOR_ORIENTATION = [True, True, False]

motors = Spirob_Motors(
	PUL, 
	DIR, 
	MOTOR_ORIENTATION, 
	steps_per_rev=1600, 
	max_rpm=30, 
	pulse_width=10 * 1e-6,
	debug=False)

vision = Vision_System()

system = Arm_System("Hysteresis_Experiment",motors,vision)

# Define Experiment Specific Tasks 

def lift_low(direction,mag):
	pos = [0,0,0]
	pos[direction] = -mag
	system.motors.move_to_steps(*pos)
	system.motors.move_to_steps(0,0,0)


if __name__ == "__main__":
	try:
		system.start()
		print("Experiment Starts")
		
		
		lift_low(1,10000)
		lift_low(1,10000)
		lift_low(1,10000)

		
		experiment_data = system.callback() 
	finally:
		system.stop()
		system.plot_post_processing()
		
		
		

	
	

