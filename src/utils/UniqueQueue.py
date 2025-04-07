import queue
from pybloom_live import BloomFilter
from threading import Lock
import gc

class uniquequeue(queue.Queue):
    def __init__(self, maxsize=0, capacity=1000000, error_rate=0.01):
        super().__init__(maxsize)
        self.capacity = capacity
        self.error_rate = error_rate
        self.bloom = BloomFilter(capacity=capacity, error_rate=error_rate)
        self.lock = Lock()

    def bf_put(self, item):
        with self.lock:
            if item not in self.bloom:
                self.bloom.add(item)
                super().put(item)

    def reset_bloom(self):
        with self.lock:
            del self.bloom
            self.bloom = BloomFilter(
                capacity=self.capacity, 
                error_rate=self.error_rate
            )
            gc.collect()
