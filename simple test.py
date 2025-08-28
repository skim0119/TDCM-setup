from gpiozero import Device, OutputDevice 
from gpiozero.pins.mock import MockFactory 
import time

# Device.pin_factory = MockFactory()

# Constants
# Front Left: Purple-17-PUL+, Blue-27-DIR+, Gray-GND
# Front Right: Orange-22-PUL+, Yellow-23-DIR+, Green-GND
# Back: Red-25-PUL+, Brown-24-DIR+, Black-GND
PUL = [17, 22, 25] 
DIR = [27, 23, 24] 
run_count = 6400
pulse_width = 5e-6
delay = 5e-4

PUL_device = [OutputDevice(pin) for pin in PUL]
DIR_device = [OutputDevice(pin) for pin in DIR]

# PUL ON = clockwise, OFF = counter clockwise (looking at face)
def pul_run(func, *args):
    for device in PUL_device:
        func(device, *args)

def dir_run(func, *args):
    for device in DIR_device:
        func(device, *args)

def set_state(device: OutputDevice, state: bool):
    if state:
        device.on()
    else:
        device.off()

def toggle(device: OutputDevice):
    device.toggle()

pul_run(set_state, False)
dir_run(set_state, False)

print(f"Running forwards {run_count} steps")
for _ in range(run_count):
    pul_run(toggle)
    time.sleep(pulse_width)
    pul_run(toggle)
    time.sleep(delay)

time.sleep(1)

print(f"Running backwards {run_count} steps")
dir_run(set_state, True)
for _ in range(run_count):
    pul_run(toggle)
    time.sleep(pulse_width)
    pul_run(toggle)
    time.sleep(delay)

print('Finished')