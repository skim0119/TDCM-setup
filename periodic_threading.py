import threading
import time
import traceback

class PeriodicThread(threading.Thread):
    """
    A thread that calls `func(*args, **kwargs)` every `interval` seconds.
    - Drift-corrected: keeps a stable schedule based on the initial start time.
    - Skips missed periods if the work overruns the interval.
    - Doesn't block the main thread (daemon=True by default).
    """
    def __init__(self, interval, func, *, args=(), kwargs=None, name=None, daemon=True):
        super().__init__(name=name or f"Periodic({interval}s)", daemon=daemon)
        self.interval = float(interval)
        self.func = func
        self.args = args
        self.kwargs = kwargs or {}
        self._stop_evt = threading.Event()

    def stop(self):
        self._stop_evt.set()

    def run(self):
        next_deadline = time.perf_counter() + self.interval
        while not self._stop_evt.is_set():
            # Sleep until the next deadline, but allow early wake-up if stopping
            remaining = next_deadline - time.perf_counter()
            if remaining > 0:
                if self._stop_evt.wait(timeout=remaining):
                    break  # stop requested during wait

            # Execute the task
            try:
                self.func(*self.args, **self.kwargs)
            except Exception:
                # Don't let exceptions kill the thread silently
                traceback.print_exc()

            # Schedule the next tick, correcting for drift/overruns
            next_deadline += self.interval
            # If we're already past the next deadline (overrun), jump forward enough periods
            behind = time.perf_counter() - next_deadline
            if behind > 0:
                # skip missed intervals to resync
                skip = int(behind // self.interval) + 1
                next_deadline += skip * self.interval
