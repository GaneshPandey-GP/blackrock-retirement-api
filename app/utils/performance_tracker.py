import time
import psutil
import os
import threading

class PerformanceTracker:
    def __init__(self):
        self.start_time = None
        self.process = psutil.Process(os.getpid())

    def start(self):
        self.start_time = time.time()

    def get_metrics(self) -> dict:
        # --- Response time ---
        elapsed_ms = (time.time() - self.start_time) * 1000
        hours, rem = divmod(int(elapsed_ms / 1000), 3600)
        minutes, seconds = divmod(rem, 60)
        millis = int(elapsed_ms % 1000)
        time_str = f"{hours:02}:{minutes:02}:{seconds:02}.{millis:03}"

        # --- Memory usage ---
        memory_mb = self.process.memory_info().rss / (1024 * 1024)
        memory_str = f"{memory_mb:.2f} MB"

        # --- Thread count ---
        thread_count = threading.active_count()

        return {
            "time": time_str,
            "memory": memory_str,
            "threads": thread_count
        }

# global singleton instance
tracker = PerformanceTracker()