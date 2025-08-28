import pigpio
import typing
import time
import matplotlib.pyplot as plt
import numpy as np
class PinSignalListener:
	# PinSignalListener
		# Basic Function For pins signal call back
		# listener must be start() before the creation of motor class
		# To avoid interfernce of pins signal
	def __init__(self,pins):
		self.pins = list(pins)
		self.being_listened_pins = []
		self.timestamps = {pin: [] for pin in self.pins}
		
		self._pi = None
		self._callbacks = {}
		self._start_time = None
	def listen_to(self,index):
		if type(index) == int:
			self.being_listened_pins.append(self.pins[index])
		else:
			for i in index:
				self.being_listened_pins.append(self.pins[i])
	
	def start(self,PLOT = True):
		#print("LLL",self.being_listened_pins)
		self._start_time = time.time()
		if self._pi is not None:
			return
		self._pi = pigpio.pi()
		pins_to_listen = self.being_listened_pins
				
		def record_pin_signal(pin):
			
			def gpio_callback(gpio,level,tick,pin = pin):
				t = time.time() - self._start_time
				self.timestamps[pin].append(t) 
	
			
			self._pi.set_mode(pin,pigpio.INPUT)
			cb = self._pi.callback(pin,pigpio.RISING_EDGE,gpio_callback)
			self._callbacks[pin] = cb
		print("self",self.being_listened_pins)
		for pin_det in self.being_listened_pins:
			print("pin",pin_det)
			record_pin_signal(pin_det)
			print("callback",self._pi,self._callbacks)
			

	def end(self,PLOT = True):
		
		if self._pi == None:
			return
		for pins, cb in self._callbacks.items():
			cb.cancel
			
		self._pi.stop()
		self._pi = None
		self._start_time = None
		
		
	def plot_pins_signal_output(self,pin):
		plot_time = [0]
		levels = []
		plot_level = [levels[0] if levels else 0]
		timestamps = np.array(self.timestamps[pin].copy())
		for t,l in zip(self.timestamps,levels):
			plot_time.extend([t,t])
			plot_level.extend([plot_level[-1],l])
		#plt.figure(figsize=(10,3))
		#plt.step(plot_time,plot_level,where = 'post')
		timestamps_freq = []
		#print(len(timestamps)-1)
		for i in range(int(len(timestamps)-1)):
			timestamps_freq.append(timestamps[i+1]-timestamps[i])
		x_values = list(range(len(timestamps_freq)))
		
		mean = np.mean(timestamps_freq)
		var = np.var(timestamps_freq)
		print("Mean",mean,"s")
		print("Varience",var)
		
		plt.figure(1)

		plt.plot(x_values,timestamps_freq)
		plt.ylim(0,0.01)
		plt.xlabel("Time")
		plt.ylabel("GPIO Level")
		plt.grid(True)
		plt.tight_layout()
		plt.legend()
		
		
		x_values2 = list(range(len(timestamps)))
		plt.figure(2)
		plt.plot(x_values2,timestamps)
		plt.grid(True)
		plt.tight_layout()
		plt.legend()
		
		plt.show()
			
