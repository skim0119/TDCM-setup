import matplotlib.pyplot as plt 
import numpy as py 
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

color_masks = {
	"Blue": [np.array([105,100,100],dtype = np.uint8),np.array([110,255,255],dtype = np.uint8)],
	"Yellow":[np.array([23,100,100],dtype = np.uint8),np.array([35,255,255],dtype = np.uint8)],
	"Orange":[np.array([8,100,100],dtype = np.uint8),np.array([20,255,255],dtype = np.uint8)],
	"Purple":[np.array([140,30,30],dtype = np.uint8),np.array([160,255,255],dtype = np.uint8)],
	"Green":[np.array([95,70,70],dtype = np.uint8),np.array([105,255,255],dtype = np.uint8)]
}

loop_blue = []
loop_yellow = []
loop_orange = []
loop_purple = []
loop_green = []

def tracker(color_mask,loop):

	lower_blue = color_mask[0]
	upper_blue = color_mask[1]

	# Imaging Processing Getting Arm Position
	image_processor.optical_flow_track(lower_blue,upper_blue)

	# Get Position with Acuation Data
	# [[frame_timestamps_i,traj_i (2) ,acuation_i (3) ],....]
	for i in range(len(image_processor.traj)):
		if image_processor.frame_timestamps[i] >= 2: # Cut the trash frame from time.sleep(2)
			item = [image_processor.traj[i]]+image_processor.traj[i] + sampling_actuation[i]
			item.pop(0)
			print(item)
			loop.append(item)
	image_processor.traj = None
	image_processor.speeds = None
	image_processor.color_mask_lower = None
	image_processor.color_mask_upper = None


path0 = Path("/home/spirob/Documents/Experiments/path_record_color_dot.txt")
path_origin = Path("home/spirob/Desktop/frame_0000.jpg")
acuation2pos_data = []
with open(path0,"r") as f:
	path_record = json.load(f)
 
# Read History Collection Data into file 

image_processor = Vision_System()

image_processor.path = Path(path_record["Vision_path"])
image_processor.statr_time = path_record["start_time"]
image_processor.frame_counter = path_record["counter"]
output_dir = Path(path_record["Exp_path"])
image_processor.frame_timestamps = path_record["timestamps"]
sampling_actuation = path_record["acuation"]


# Processing Different Color Dots 
tracker(color_masks["Blue"],loop_blue)
tracker(color_masks["Yellow"],loop_yellow)
tracker(color_masks["Orange"],loop_orange)
tracker(color_masks["Purple"],loop_purple)
tracker(color_masks["Green"],loop_green)


loop_blue = np.array(loop_blue)
loop_yellow = np.array(loop_yellow)
loop_orange = np.array(loop_orange)
loop_purple = np.array(loop_purple)
loop_green = np.array(loop_green)


"""
plt.figure(1)

plt.plot(1000*loop_blue[:,4],loop_blue[:,1],color = 'blue', label = "Unit 1",lw = 1.5)


plt.plot(1000*loop_blue[:,4],loop_yellow[:,1],color = 'yellow', label = "Unit 5",lw = 1.5)
plt.plot(1000*loop_blue[:,4],loop_orange[:,1],color = 'orange', label = "Unit 10",lw = 1.5)
plt.plot(1000*loop_blue[:,4],loop_purple[:,1],color = 'purple', label = "Unit 15",lw = 1.5)
plt.plot(1000*loop_blue[:,4],loop_green[:,1],color = 'green', label = "Unit 18",lw = 1.5)

#plt.plot(10000*data[:,5],data[:,2], color = 'black',label = "Motor2")
plt.xlabel("Accuation (mm)")
plt.ylabel("Position y (pixels)")
plt.grid(True)
plt.tight_layout()
plt.legend()
"""

fig, ax = plt.subplots()
#sc = ax.scatter(data[:,1],data[:,2],c = data[:,0],cmap = 'viridis', label = "Motor0", s=18,marker = '+')
sc = ax.scatter(loop_blue[:,1],loop_blue[:,2],c = 'red', label = "* Unit 1",s = 18,marker = '*')
 
sc = ax.scatter(loop_yellow[:,1],loop_yellow[:,2],c = 'blue',label = "Unit 5",s = 18,marker = 'x')
sc = ax.scatter(loop_orange[:,1],loop_orange[:,2],c = 'black', label = "Unit 10",s = 18,marker = 's')
sc = ax.scatter(loop_purple[:,1],loop_purple[:,2],c = 'green', label = "Unit 15",s = 18,marker = '^')
sc = ax.scatter(loop_green[:,1],loop_green[:,2],c = 'orange', label = "Unit 18",s = 18,marker = 'o')
#cb = plt.colorbar(sc,ax = ax)
#cb.set_label("Time (s)",rotation = 270, labelpad = 15)
ax.set_xlabel("Position X (pixels) ")
ax.set_ylabel("Position Y (pixels)")
ax.set_title("Position X via Position Y")
ax.legend()

"""
plt.figure(3)
plt.plot(data[:,0],label = "time")
plt.grid(True)
plt.tight_layout()
plt.legend()

fig, ax = plt.subplots()
sc = ax.scatter(data[:,1],data[:,2],c = data[:,0],cmap = 'viridis', label = "Motor0", s=18)
cb = plt.colorbar(sc,ax = ax)

ax.set_xlabel("Position X (pixels)")
ax.set_ylabel("Position Y (pixels)")
ax.set_title("Position Colored by time")
"""

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




