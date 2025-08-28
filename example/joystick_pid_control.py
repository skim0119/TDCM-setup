from joystick_controller import Joystick_Controller
from PID_controller import PID_controller
from motor_advance import Spirob_Motors
import threading
import time
import numpy as py
from threading import Event
import math
import matplotlib.pyplot as plt 
class Power_Motor(Spirob_Motors):
	
	def __init__(self,*args, **kwargs):
			super().__init__(*args,**kwargs)
			self.start_flag = None
			self.config = [0,-3000,0,1] # (x,y,z,speed)
	def move_to(self):
		
		coords = [0,300,0]
		#print("Moving the Arm to Target Position...")
		for motor_index in range(len(self._PUL_devices)):
			#print(motor_index)
			if self.num_of_steps[motor_index] - coords[motor_index]> 0:
				 self.dir_motor_backward([motor_index])
				 self.set_motor_speed([motor_index], 1)
				 self.start_motor([motor_index])
			elif self.num_of_steps[motor_index] - coords[motor_index]< 0:
				 self.dir_motor_forward([motor_index])
				 self.set_motor_speed([motor_index], 1)
				 self.start_motor([motor_index])
		self.set_motor_speed([0], 0)
		self.set_motor_speed([2], 0)
		try:
			while True:
				self.start_time = time.time()
				#print(self.config)
				Action = True		
				#print("tar",self.config[1],"cur",self.num_of_steps[1])
				with threading.Lock():
					#self.set_motor_speed([0], 0)
					#print(min(1,abs(self.config[3])))
					self.set_motor_speed([1], abs(self.config[3]))
					#self.set_motor_speed([2], 0)
		
				#print("gap",self.config[1] - self.num_of_steps[1])
				#print("motor_running",self._motor_running)
				if self.config[1] - self.num_of_steps[1]> 0:
					self.dir_motor_forward([1])
				else:
					self.dir_motor_backward([1])
				#self.start_flag.clear()
				#start = time.time()
			
				#current_step0 = self.num_of_steps[0]
				current_step1 = self.num_of_steps[1]
				#current_step2 = self.num_of_steps[2]	
				#gap_step0 = self.config[0] - current_step0
				gap_step1 = self.config[1] - current_step1
				#gap_step2 = self.config[2] - current_step2
				#print("Target",self.config[1],"Cur",current_step1,"speed",self._motor_speeds)
				if gap_step1 == 0: 
					pass
				self.update([0,1,2])
				#time.sleep(0.1)
				#print("gap_step1",gap_step1,"start flag",self.start_flag)
				"""
				if gap_step1 == 0 or time.time() - start > 0.5:
					print("Reached")
					self.start_flag.set()
					Action = False
					#time.sleep(0.001)
				"""
			
					
		except KeyboardInterrupt:
			print("\nMain loop interrupted by Ctrl+C.")
		finally:
			print(self.motor_direction)
			print(self.num_of_steps)



class System:
	def __init__(self,
		js: Joystick_Controller,
		motors: Power_Motor,
		controller: PID_controller):
			self.js = js
			self.motors = motors
			self.controller = controller
			self.speed = 0.0
			self.y_axis = 0.0
			self.start_time = time.time()
			
			# 	Create stop_flag to cooridnate threads, pass flag to motors and js
			self.start_flag = Event()
			self.start_flag.set()
			self.js.start_flag = self.start_flag
			self.motors.start_flag = self.start_flag
			self.speed_collection = []
			
	def start(self):
		def main_loop():
			freq = 20
			while True:
				#print("[main]",self.start_flag)
				#self.start_flag.wait()
				#print("d")
				now = time.time() - self.start_time
				cur = self.motors.get_current_feedback()["Steps"][1]
				start_time = time.time()
				with threading.Lock():
					#self.y_axis = self.js.latest_xy[1]
					#print("update from js")
					self.motors.config[1] = int(self.js.latest_xy[1] * 4000)
					print("tar",self.motors.config[1],"cur",cur)
					#self.motors.config[1] = -1000
					#print("speed",self.controller.step(self.motors.config[1],cur,now)/10000000)
					#self.motors.config[3] = min(1,abs(self.controller.step(self.motors.config[1],cur,now))/10000000)
					self.motors.config[3] =sigmo(self.controller.step(self.motors.config[1],cur,now),-10000,10000)
					
					print("speed",self.motors.config[3])
					self.speed_collection.append(self.motors.config[3])
			
				sleep_for = (1/freq) - ((time.time()-start_time)%(1/freq))
				
				if sleep_for > 0:
					time.sleep(sleep_for)
					
		def sigmo(x,L,H,alpha = 0.01):
			x0 = (L + H) /2
			k = 2 * math.log((1-alpha)/alpha)/ (H - L)
			return ((1 / (1 + (math.e**(-k*(x-x0)))))-0.5)*2

				#time.sleep(0.01)
	
		self.js.init(motor_position = self.motors.history_collection)

		t_motor = threading.Thread(target = self.motors.move_to,daemon = True)
		t_main = threading.Thread(target = main_loop,daemon = True)
		#t_motor.start()
		t_main.start()
		t_motor.start()
		self.js.start()
		
		#t_motor.join()
		#t_main.join()
		

		
		try:
			print("Main_loop")
		except KeyboardInterrupt:
			print("End")
		finally:
			plt.plot(self.speed_collection)
			plt.show()
	
		
if __name__ == "__main__":
	
	
	PUL = [17, 25, 22] 
	DIR = [27, 24, 23] 
	MOTOR_ORIENTATION = [True, True, False]

	controller = PID_controller(kp = 2.5, ki = 0, kd= 1)

		
	js = Joystick_Controller(freq = 20)


	motors = Power_Motor(
		PUL, 
		DIR, 
		MOTOR_ORIENTATION, 
		steps_per_rev=3200, 
		max_rpm=60, 
		pulse_width=10 * 1e-6,
		debug=False)

	system = System(js,motors,controller)
	system.start()
