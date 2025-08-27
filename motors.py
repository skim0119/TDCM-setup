from gpiozero import Device, OutputDevice
from gpiozero.pins.mock import MockFactory
# import asyncio
import warnings
import time
import typing
from collections.abc import Callable

class Motors:
    def __init__(self, 
        pul_pins: list[int], 
        dir_pins: list[int], 
        motor_orientation: list[bool],
        steps_per_rev: int = 400,
        max_rpm: float = 60.,
        pulse_width: float = 10e-6, 
        debug: bool = False
    ):
        """
        motor_orientation -- True means dir_motor_forward is clockwise when looking at the motor face
        """
        if debug:
            Device.pin_factory = MockFactory()
        assert len(pul_pins) == len(dir_pins) == len(motor_orientation)
        self.pul_pins = pul_pins
        self._PUL_devices = [OutputDevice(pin) for pin in pul_pins]
        self._DIR_devices = [OutputDevice(pin) for pin in dir_pins]
        self.motor_orientation = motor_orientation
        self.steps_per_rev = steps_per_rev
        self.max_rpm = max_rpm
        self.pulse_width = pulse_width
        
        # 0 to 1 of max_rpm
        self._motor_speeds: list[float] = [0] * len(pul_pins)
        self._motor_running: list[bool] = [False] * len(pul_pins)
        
        self._pulse_counter_targets: list[int] = [-1, -1, -1] * len(pul_pins)
        self._pulse_in_high_phase: bool = False

        # check if RPM is too high
        min_step_time = 2 * self.pulse_width
        max_steps_per_s = 1 / min_step_time
        abs_max_rpm = max_steps_per_s * 60 / steps_per_rev
        if self.max_rpm > abs_max_rpm:
            warnings.warn(f"Max RPM of {max_rpm} is too high, defaulting to {abs_max_rpm:.2f} RPM")
            self.max_rpm = abs_max_rpm

        self.motor_direction: list[bool] = [True] * len(pul_pins)        
        self.num_of_steps = [0] * len(pul_pins)

    def _get_pulse_low_time(self, scale: float):
        """Get delay corresponding to scale * max_rpm"""
        assert 0 <= scale <= 1
        if scale == 0:
            warnings.warn("Received pulse low time request at 0 speed, delaying by 1s")
            return 1
        # rev/min * min/60s * steps/rev = steps/s -> in 1 second it needs this many steps
        # 1s = steps * (pulse_width + delay) -> 1/steps - pulse_width = delay
        steps_per_s = scale * self.max_rpm / 60 * self.steps_per_rev
        delay = 1/steps_per_s - self.pulse_width
        return delay
    
    def _run(self, variable_list: list[typing.Any], index: typing.Union[int, list[int]], func: Callable[[typing.Any, int], None]):
        if type(index) == int:
            self._validate_motor_index(index)
            return func(variable_list[index], index)
        else:
            results = []
            for i in index:
                self._validate_motor_index(i)
                results.append(func(variable_list[i], i))
            return results
        
    def set_motor_speed(self, motor_index: typing.Union[int, list[int]], speed: float) -> None:
        """Set motor speed (0 to 1) of motor at motor_index"""
        assert 0 <= speed <= 1
        def set_speed(_, index):
            self._motor_speeds[index] = speed

        self._run(self._motor_speeds, motor_index, set_speed)
    
    def _pul_motor_on(self, motor_index: typing.Union[int, list[int]]):
        self._run(self._PUL_devices, motor_index, lambda d, _: d.on())

    def _pul_motor_off(self, motor_index: typing.Union[int, list[int]]):
        self._run(self._PUL_devices, motor_index, lambda d, _: d.off())

    def dir_motor_forward(self, motor_index: typing.Union[int, list[int]]):
        def motor_forward(device, index):
            if self.motor_orientation[index]:
                device.on()
            else:
                device.off()
            self.motor_direction[index] = True
        self._run(self._DIR_devices, motor_index, motor_forward)

    def dir_motor_backward(self, motor_index: typing.Union[int, list[int]]):
        def motor_backward(device, index):
            if self.motor_orientation[index]:
                device.off()
            else:
                device.on()
            self.motor_direction[index] = False
        self._run(self._DIR_devices, motor_index, motor_backward)

    def start_motor(self, motor_index: typing.Union[int, list[int]]):
        def set_motor_running(_, index):
            self._motor_running[index] = True
        self._run(self._motor_running, motor_index, set_motor_running)

    def stop_motor(self, motor_index: typing.Union[int, list[int]]):
        def set_motor_running(_, index):
            self._motor_running[index] = False
        self._run(self._motor_running, motor_index, set_motor_running)

    def _validate_motor_index(self, index):
        assert 0 <= index < len(self._PUL_devices), "Index out of range for given pins"



    def update(self, motor_index: typing.Union[int, list[int]]) -> int:
        """
        Check any running counters and give pulse if necessary. For use in main loop.
        Returns -- 1 if switched to high, -1 if switched to low, 0 if no change
        """
        def check_counter(device, index):
            if not self._motor_running[index] or self._motor_speeds[index] == 0:
                return 0
            
            if time.perf_counter_ns() >= self._pulse_counter_targets[index]:
                if self._pulse_in_high_phase:
                    device.off()
                    self._pulse_in_high_phase = False
                    self._pulse_counter_targets[index] = time.perf_counter_ns() + \
                        self._get_pulse_low_time(self._motor_speeds[index]) * 1e9
                    return -1
                else:
                    device.on()
                    if self.motor_direction[index] == True: self.num_of_steps[index] += 1
                    else: self.num_of_steps[index] -= 1
        
                    self._pulse_in_high_phase = True
                    self._pulse_counter_targets[index] = time.perf_counter_ns() + \
                        self.pulse_width * 1e9
                    return 1
            return 0
        return self._run(self._PUL_devices, motor_index, check_counter)

    

    
    


