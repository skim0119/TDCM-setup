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
	debug=False, 
	speed = 1)

vision = Vision_System()

system = Arm_System("Hysteresis_Experiment_test",motors,vision)

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
		
		motors.speed = 0.8
		#time.sleep(5)
		lift_low(1,4000)
		lift_low(1,4000)
		lift_low(1,4000)
		#lift_low(1,6000)
		#lift_low(1,6000)
		#lift_low(1,6000)
		#lift_low(1,6500)
		#lift_low(1,7000)
		#lift_low(1,7500)
		##motors.speed = 0.25
		#lift_low(1,8000)
		experiment_data = system.callback() 
	finally:
		system.stop()
		system.plot_post_processing()
		
		
		

	
	

