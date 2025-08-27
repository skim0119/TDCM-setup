from motor_advance import Spirob_Motors
from vision_capture import Vision_System
import numpy as np
import time
from datetime import datetime
from typing import Callable, List
from datetime import datetime
from pathlib import Path
import os
import json
from periodic_threading import PeriodicThread
import matplotlib.pyplot as plt
class Arm_System:
	def __init__(
		self,
		experiment_name,
		motors: Spirob_Motors,
		vision: Vision_System
	):
		self.experiment_name = experiment_name
		self.motors = motors
		self.vision = vision
		self.start_time = None
		now = datetime.now()
		self.output_dir = Path(f"/home/spirob/Documents/Experiments/{experiment_name}{now}")
		self.camera_dir = Path(os.path.join(self.output_dir,"Vision"))
		self.current_acuation = self.motors.num_of_steps
		self.sampling_actuation = []
		self.actuation2pos_data = []

	def start(self):
		print("Experiment Starts")
		self.start_time = time.time()
		self.vision.start_time = self.start_time
		self.output_dir.mkdir(parents=True,exist_ok=True)
		self.camera_dir.mkdir(parents=True,exist_ok=True)
		self.real_time_feedback(20, Animation = False)
		self.vision.path = self.camera_dir
		time.sleep(2) # Wait for the muti threading to start

	def stop(self):
		self.listener.stop()
		# Write History Collection Data into file 
		file_path = os.path.join(self.output_dir,"result.txt")
		file_path2 = os.path.join(self.output_dir,"sampling.txt")
		for key in self.motors.history_collection:
			self.motors.history_collection[key] = self.motors.history_collection[key][250:]
			
		with open(file_path, "w") as f:
			json.dump(self.motors.history_collection,f,indent = 1)
		with open(file_path2,"w") as f:
			json.dump(self.sampling_actuation,f)
		print("Experiment Ends")
		
		
		# Imaging Processing Getting Arm Position
		self.vision.optical_flow_track()
		
		# Get Position with Acuation Data
		# [[frame_timestamps_i,traj_i (2) ,acuation_i (3) ],....]
		for i in range(len(self.vision.traj)):
			if self.vision.frame_timestamps[i] >= 2: # Cut the trash frame from time.sleep(2)
				item = [self.vision.frame_timestamps[i]]+self.vision.traj[i] + self.sampling_actuation[i]
				item.pop(0)
				print(item)
				self.actuation2pos_data.append(item)
			
	
	def real_time_feedback(self,freq = 10, Animation = False): 
		def get_current_feedback():
			actuation_feedback = self.motors.get_current_feedback()
			#print(actuation_feedback["Distance"])
			self.sampling_actuation.append(actuation_feedback["Distance"])
			self.vision.capture_frame() # Capture a Frame
		
		self.listener = PeriodicThread(1/freq, get_current_feedback)
		self.listener.start()
		

	def callback(self):
		
		feedback = self.motors.history_collection
		return feedback
	
	def plot_post_processing(self): 
		
		#print("vision",self.vision.traj)
		# Ploting Accuation Graph
		
		data = np.array(self.actuation2pos_data.copy())
		
	
		plt.figure(1)
	
		#plt.plot(10000*data[:,3],data[:,1],color = 'r', label = "Motor0")
		plt.plot(10000*data[:,4],data[:,1],color = 'blue', label = "Motor=1")
		#plt.plot(10000*data[:,5],data[:,1], color = 'black',label = "Motor2")
		plt.xlabel("Accuation")
		plt.ylabel("Position x")
		plt.grid(True)
		plt.tight_layout()
		plt.legend()


		plt.figure(2)
		#plt.plot(10000*data[:,3],data[:,2],color = 'r', label = "Motor0")
		plt.plot(10000*data[:,4],data[:,2],color = 'blue', label = "Motor=1")
		#plt.plot(10000*data[:,5],data[:,2], color = 'black',label = "Motor2")
		plt.xlabel("Accuation")
		plt.ylabel("Position y")
		plt.grid(True)
		plt.tight_layout()
		plt.legend()
		
		plt.figure(3)
		plt.plot(data[:,1],data[:,2],color = 'r', label = "Motor0")
	
		plt.xlabel("Position X")
		plt.ylabel("Position Y")
		plt.grid(True)
		plt.tight_layout()
		plt.legend()
		
		"""
		print(np.array(self.sampling_actuation))
		plt.figure(1)
		
		plt.plot(10000*np.array(self.sampling_actuation)[:,0],color = 'r', label = "Motor0")
	
		plt.xlabel("Accuation")
		plt.ylabel("Position x")
		plt.grid(True)
		plt.tight_layout()
		plt.legend()
		"""
		plt.show()
		

