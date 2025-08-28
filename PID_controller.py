from joystick_controller import Joystick_Controller
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import collections


class PID_controller:
	def __init__(self,
		kp: float,
		ki: float,
		kd: float		
	):
		self.kp = kp
		self.ki = ki
		self.kd = kd
		self.integrator = 0.0 
		self.prev_time = None
		self.prev_step = None
	def reset(self):
		self.integrator = 0.0
		self.prev_time = None 
		
	def step(self, target_step, current_step, time) -> float:
		
		error = target_step - current_step
		if self.prev_time:
			dt = time - self.prev_time
		else:
			self.prev_time = time
			self.prev_step = current_step
			dt = 10e-6
		
		self.integrator += error * dt
		diff = current_step - self.prev_step
		self.prev_step = current_step
		
		output = self.kp * error  + self.ki * self.integrator + self.kd * diff
		#print("output",output)
		#print("error",error)
		return output
