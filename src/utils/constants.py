from . import UniqueQueue
import queue


raw_proxy_queue = UniqueQueue.uniquequeue()
usable_proxy_queue = UniqueQueue.uniquequeue()
crawler_task_queue = queue.Queue()
PER = 60
