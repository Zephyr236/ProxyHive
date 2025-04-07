import threading
import weakref
from colorama import Fore
import logging
from src.utils import *
from concurrent.futures import ThreadPoolExecutor, as_completed


class CrawlerTask(threading.Thread):
    def __init__(self, usable_proxy_queue, crawler_task_queue, max_workers=5):
        super().__init__()
        self.crawler_task_queue_ref = weakref.proxy(crawler_task_queue)
        self.usable_proxy_queue_ref = weakref.proxy(usable_proxy_queue)
        self.stop_flag = False
        self.event = threading.Event()
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(self.max_workers)
        self.all_task = []

    def run(self):
        while not self.stop_flag:
            try:
                if self.stop_flag:
                    break

                if not self.stop_flag:
                    data = self.crawler_task_queue_ref.get(timeout=20)
                    if data is None:
                        continue
                    spider = CrawlerWorker.CrawlerWorker(
                        self.usable_proxy_queue_ref,
                        self.crawler_task_queue_ref,
                        data["task"],
                        data["file_id"],
                    )

                    if len(self.all_task) < self.max_workers:
                        if not self.stop_flag:
                            future = self.executor.submit(spider.run)
                            self.all_task.append(future)
                            self.spider_refs[future] = spider
                    else:
                        for future in as_completed(self.all_task):
                            self.all_task.remove(future)
                            spider_done = self.spider_refs.pop(future, None)
                            if spider_done is not None:
                                del spider_done

                            if not self.stop_flag:
                                future = self.executor.submit(spider.run)
                                self.all_task.append(future)
                                self.spider_refs[future] = spider
                            break
            except:
                pass

    def stop(self):
        self.stop_flag = True
        self.event.set()
        self.executor.shutdown(wait=True)
