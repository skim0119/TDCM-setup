import numpy as np
import time
import threading
from threading import Event
import pygame
from motor_advance import Spirob_Motors
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle
import os, collections, signal, sys

class Joystick_Controller:
	def __init__(self
	,freq):
		self.js = None
		self.window_sec = 8
		self.sampling_freq = freq
		self.Sample = [float,float,float]
		self.input_collection: Deque[self.Sample] = collections.deque(maxlen = int(self.sampling_freq * self.window_sec))
		self.latest_xy = [0.0, 0.0]
		self.start_time = None
		self.data_lock = threading.Lock()
		self.ani = None
		self.start_flag = None
		self.motor_position_collection = None

		
	def init(self,motor_position):
		 pygame.init()
		 pygame.joystick.init()
		 self.js = pygame.joystick.Joystick(0)
		 self.js.init()
		 self.start_time = time.time()
		 self.motor_position_collection = motor_position
		 #self.start_flag.set()
	
	def start(self):
		#t1 = threading.Thread( target = self.controller_feedback_plot,daemon = True)
		#self.start_flag.wait()
		t2 = threading.Thread(target = self.joystick_listener,daemon = True)
		#`t1.start()
		t2.start()
		self.controller_feedback_plot()
			 
		try:
			plt.show()
	
		except KeyboardInterrupt:
			print("KeyboardInterrupt")
		finally:
			pass
	def joystick_listener(self):
		AXIS_X = 0 
		AXIS_Y = 1
		smooth_x = 0
		smooth_y = 0
		smooth_coef = 0.95
		while True:
			#print("[js]",self.start_flag)
			#self.start_flag.wait()
			pygame.event.pump()
			#if self.js.get_button(0) : print("press")
			t = time.time() - self.start_time
			#print(self.js.get_axis(AXIS_Y))
			smooth_x = (1-smooth_coef) * float(self.js.get_axis(AXIS_X)) + smooth_coef * smooth_x
			smooth_y = (1-smooth_coef) * (-float(self.js.get_axis(AXIS_Y))) + smooth_coef * smooth_y
			with self.data_lock:
				self.latest_xy[0] = smooth_x
				self.latest_xy[1] = smooth_y
				self.input_collection.append((t,self.latest_xy[0],self.latest_xy[1],self.motor_position_collection["Steps"][-1][1]))
			now = time.time()
			sleep_for = (1/self.sampling_freq)- ((now - self.start_time)% (1/self.sampling_freq))
		#print(sleep_for)
			if sleep_for > 0:
				time.sleep(sleep_for)
		
	def controller_feedback_plot(self):
		#print("Runing Feedback")
		fig = plt.figure(figsize = (9,6))
		gs = fig.add_gridspec(nrows = 2, ncols = 1, height_ratios = [1,1.2],hspace = 0.3)
		ax_dot = fig.add_subplot(gs[0,0])
		ax_ts = fig.add_subplot(gs[1,0])
		
		
		
		circle = Circle((0,0),radius = 1, fill =False, linewidth = 1.5)
		ax_dot.add_patch(circle)
		dot_plot, = ax_dot.plot([],[],'o',ms = 8, mec='k',mfc = 'r')
		
		ax_dot.set_aspect('equal', adjustable = 'box')
		ax_dot.set_xlim(-1.1,1.1)
		ax_dot.set_ylim(-1.1,1.1)
		ax_dot.grid(True,alpha=0.3)
		ax_dot.set_xlabel("X")
		ax_dot.set_ylabel("Y")
		
		# (2) Scrolling time-series panel
		line_y, = ax_ts.plot([],[],lw = 1.5, label = 'Axis Y')
		ax_ts.set_ylim(-1.05,1.05)
		ax_ts.set_xlim(0,self.window_sec)
		ax_ts.set_xlabel("Time(s)")
		ax_ts.set_ylabel("Y (norm)")
		ax_ts.grid(True,alpha = 0.3)
		
		# (3) Scrolling time-seris for Motor Steps
		line_motor, = ax_ts.plot([],[],lw = 1.5, label = "Motor Position", color = 'r')
		ax_ts.legend(loc = "upper right")
		#timer = None
		def animate(_frame):
			#print("Update",_frame/(time.time()-self.start_time))
			#print(self.data_lock.locked())
			"""
			if self.start_flag.is_set():
				if timer:
					print("[js] animation start")
					timer.event_source.start()
				
			if not self.start_flag.is_set():
				if timer:
					timer.event_source.stop()
				print("[js] animation stop")
			"""
			#print("input_collection",np.array(self.input_collection)[-1,-1])
			
			with self.data_lock:
				if self.input_collection:
					t_last = self.input_collection[-1][0]
					t_min = max(0.0,t_last - self.window_sec)
					
					ts,ys,motor_s = [], [], []
					for t,_x,y,ms in self.input_collection:
						if t >= t_min:
							ts.append(t)
							ys.append(y)
							motor_s.append(ms/4000)
					
					
				else:
					t_last = 0.0 
					ts,ys,motor_s = [],[],[]
			#print("input_collection",motor_s)
			x_cur = self.latest_xy[0]
			y_cur = self.latest_xy[1]
			#print([x_cur],[y_cur])
			dot_plot.set_data([x_cur],[y_cur])
			
			if ts:
				#print("set")
				line_y.set_data(ts,ys)
				line_motor.set_data(ts,motor_s)
				ax_ts.set_xlim(max(0.0,ts[-1]-self.window_sec),ts[-1])
				
			return	dot_plot, line_y , line_motor
		
		#self.ani = FuncAnimation(fig,animate, interval = 200, blit = True)
		#timer = self.ani 
"""
joy = Joystick_Controller(freq = 20)
joy.init()
joy.start()
"""
