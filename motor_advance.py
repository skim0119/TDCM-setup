from motors import Motors 
from motor_signal_detector import PinSignalListener
import numpy as np
import time
import typing
from periodic_threading import PeriodicThread


class Spirob_Motors(Motors):
	def __init__(self,pul_pins,dir_pins,motor_orientation, PSL = False,RTSA = False ,**kwargs):
		self.history_collection = {"Times":[],"Steps":[],"Distance":[],"Speed":[],"Acceleration":[]}
		# Capping for history_collection for 20 empty data points
		for i in range(250):
			self.history_collection["Times"].append(0)	
			self.history_collection["Steps"].append([0,0,0])
			self.history_collection["Distance"].append([0,0,0])
			self.history_collection["Speed"].append([0,0,0])
			self.history_collection["Acceleration"].append([0,0,0])
			self.pul_pins = pul_pins
			self.Enable_Real_Time_Speed_Acceleration = RTSA
			self.current_feedback = None
		#self.history_collection = {index: dataset for index in range(len(self.pul_pins))}
		if PSL == True:
			self.pin_listener = PinSignalListener(self.pul_pins)
			self.pin_listener.listen_to(list(range(len(self.pul_pins))))
			self.pin_listener.start()	
		
		super().__init__(pul_pins,dir_pins,motor_orientation,**kwargs)
		#self.sub_tick = self.tick
		self.start_time = time.time()
	
	
	def update(self, motor_index: typing.Union[int, list[int]]) -> int:
		#self.update_history_collection()
		check = super().update(motor_index)
		#print(check)
		if check[0] == 1 or check[1] ==1 or check[2]==1:	
			
			self.update_history_collection()
			#print(check)

	def real_time_feedback(self,freq = 20, Animation = False): # Animation is not working, need debuging
		
		if Animation:
			self._start_rt_animation(window_s=10.0, fps=30)
		listener = PeriodicThread(1/freq, self.get_current_feedback)
		listener.start()
		

	def get_current_feedback(self):
			current_feedback = {}
			current_feedback["Times"]=time.time()-self.start_time
			current_feedback["Steps"]=self.num_of_steps.copy()
			current_feedback["Distance"]=self._get_motor_distance()
		
			vel, acc = self._get_moter_speed_acceleration_real_time()
			current_feedback["Speed"] = vel
			current_feedback["Acceleration"] = acc
			self.current_feedback = current_feedback
			#print("feedback",self.current_feedback) 
			return current_feedback
		
	def _get_moter_speed_acceleration_real_time(self):
		# Use linear Regress for the Tay =lor expasion of x(t) = a0 + a1 * t + a2 * t^2
		past_data = np.array([])
		n = 4
		time_data_past = np.array([])
		distance_data_past = np.array([])
		for i in range(n):
			time_data_temp = np.array(self.history_collection["Times"][-1-(50*n)+(50*i)])
			distance_data_temp = np.array(self.history_collection["Distance"][-1-(50*n)+(50*i)])
			time_data_past = np.append(time_data_past,time_data_temp)
			distance_data_past = np.append(distance_data_past,distance_data_temp)
		one_matrix = np.full((n),1)
		time_data_past = time_data_past - time_data_past[-1]
		distance_data_past = distance_data_past.reshape(n, 3)
		A = np.array([one_matrix,np.power(time_data_past,1), np.power(time_data_past,2)]).T
		C, *_ = np.linalg.lstsq(A,distance_data_past,rcond = None)
		velocity = C[1,:]
		acceleration = 2 * C[2,:]
		
		return velocity, acceleration
	
	
	def _get_motor_distance(self):
		diameter = 0.015
		step_position = self.num_of_steps.copy()
		step_distance = [(diameter/1600)*x for x in step_position] # Diameter of Threading dived by 1600 step/rev
		return step_distance
		
	def _get_moter_acceleration(self):
		print("CallBack")

	def update_history_collection(self):
		self.history_collection["Times"].append(time.time()-self.start_time)	
		self.history_collection["Steps"].append(self.num_of_steps.copy())
		self.history_collection["Distance"].append(self._get_motor_distance())
		if self.Enable_Real_Time_Speed_Acceleration:
			vel, acc = self._get_moter_speed_acceleration_real_time()
			self.history_collection["Speed"].append(vel)
			self.history_collection["Acceleration"].append(acc)
			#print(self.history_collection["Distance"][-1])
	
	def _start_rt_animation(self, window_s=10.0, fps=30):
		import numpy as np
		import matplotlib.pyplot as plt
		from matplotlib.animation import FuncAnimation
		from collections import deque

		n_motors = len(self.num_of_steps)
		self._rt_times = deque(maxlen=20000)
		self._rt_dists = [deque(maxlen=20000) for _ in range(n_motors)]
		self._rt_last_t = {'v': None}

		# keep references on self
		self._fig, self._ax = plt.subplots()
		self._lines = [self._ax.plot([], [], label=f"Motor {i}")[0] for i in range(n_motors)]
		self._ax.set_xlabel("Time (s)")
		self._ax.set_ylabel("Distance")
		self._ax.legend(loc="upper left")
		self._ax.grid(True, linestyle=":", linewidth=0.5)

		def _ingest():
			cf = getattr(self, "current_feedback", None)
			if not cf:
				return False
			t = float(cf["Times"])
			if self._rt_last_t["v"] is not None and t == self._rt_last_t["v"]:
				return False
			self._rt_last_t["v"] = t
			self._rt_times.append(t)
			dist = np.asarray(cf["Distance"], dtype=float)
			for i in range(n_motors):
				self._rt_dists[i].append(dist[i])
			return True

		def _windowed():
			if not self._rt_times:
				return None, None
			t_arr = np.fromiter(self._rt_times, dtype=float)
			t_last = t_arr[-1]
			left, right = t_last - window_s/2.0, t_last + window_s/2.0
			mask = (t_arr >= left) & (t_arr <= right)
			t_win = t_arr[mask]
			d_win = []
			for i in range(n_motors):
				di = np.fromiter(self._rt_dists[i], dtype=float)
				d_win.append(di[mask] if di.size == t_arr.size else di[-t_win.size:])
			return t_win, d_win

		def _init():
			self._ax.set_xlim(0, window_s)
			self._ax.set_ylim(-1, 1)
			for ln in self._lines:
				ln.set_data([], [])
			return self._lines

		def _update(_):
			_ingest()
			t_win, d_win = _windowed()
			if t_win is None or t_win.size == 0:
				return self._lines
			t_last = t_win[-1]
			self._ax.set_xlim(t_last - window_s/2.0, t_last + window_s/2.0)

			y_min = y_max = None
			for i, ln in enumerate(self._lines):
				ln.set_data(t_win, d_win[i])
				if d_win[i].size:
					ymin_i = float(d_win[i].min())
					ymax_i = float(d_win[i].max())
					y_min = ymin_i if y_min is None else min(y_min, ymin_i)
					y_max = ymax_i if y_max is None else max(y_max, ymax_i)
			if y_min is not None and y_max is not None:
				pad = 0.05 * max(1e-9, y_max - y_min)
				self._ax.set_ylim(y_min - pad, y_max + pad)
			return self._lines

		# keep the animation object on self to prevent GC
		self._anim = FuncAnimation(self._fig, _update, init_func=_init,
								   interval=1000.0/float(fps), blit=False)
		# non-blocking show; you must keep the main loop alive (see B)
		import matplotlib.pyplot as plt
		plt.show(block=False)

			
	def move_to_steps(self,x,y,z):
		
		coords = [x,y,z]
		print("Moving the Arm to Target Position...")
		for motor_index in range(len(self._PUL_devices)):
			print(motor_index)
			if self.num_of_steps[motor_index] - coords[motor_index]> 0:
				 self.dir_motor_backward([motor_index])
				 self.set_motor_speed([motor_index], 1)
				 self.start_motor([motor_index])
			elif self.num_of_steps[motor_index] - coords[motor_index]< 0:
				 self.dir_motor_forward([motor_index])
				 self.set_motor_speed([motor_index], 1)
				 self.start_motor([motor_index])
			target = [x,y,z]
			Action = True		
		try:
			while Action == True:
				current_step0 = self.num_of_steps[0]
				current_step1 = self.num_of_steps[1]
				current_step2 = self.num_of_steps[2]	
				gap_step0 = target[0] - current_step0
				gap_step1 = target[1] - current_step1
				gap_step2 = target[2] - current_step2
				self.update([0,1,2])
				if gap_step0 == 0:
					self.stop_motor([0])
				if gap_step1 == 0:
					self.stop_motor([1])
					Action = False
				if gap_step2 == 0:
					self.stop_motor([2])	
				if np.sum(self._motor_running) == 0:
					print("The process is done")
					Action = False
				#time.sleep(0.001)
					
		except KeyboardInterrupt:
			print("\nMain loop interrupted by Ctrl+C.")
		finally:
			self.stop_motor([0, 1, 2])
			print(self.motor_direction)
			print(self.num_of_steps)

		print("Arm has been Homed")
		
