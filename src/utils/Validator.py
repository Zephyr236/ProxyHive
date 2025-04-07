import threading
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore
import logging
import gc


class ProxyValidator(threading.Thread):

    def __init__(self, raw_proxy_queue, usable_proxy_queue, max_workers=50):
        super().__init__()
        self.raw_proxy_queue = raw_proxy_queue
        self.usable_proxy_queue = usable_proxy_queue
        self.stop_flag = False
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(self.max_workers)
        self.all_task = []
        self.event = threading.Event()



    def is_valid_proxy(self, proxy):
        if self.event.is_set():
            return
        try:
            proxies = {"http": proxy, "https": proxy}

            with requests.get(
                "https://ifconfig.info", proxies=proxies, timeout=20
            ) as response:
                if response.status_code == 200:
                    self.usable_proxy_queue.bf_put(proxy)
                    logging.info(Fore.GREEN + f"[+] Valid proxy: {proxy}" + Fore.RESET)

        except Exception as e:
            pass


    def run(self):

        while not self.stop_flag:
            proxy = self.raw_proxy_queue.get()
            if proxy:
                self.raw_proxy_queue.task_done()
            else:
                continue

            if self.stop_flag:
                continue

            if not self.stop_flag:
                if len(self.all_task) < self.max_workers:
                    if not self.stop_flag:
                        future = self.executor.submit(self.is_valid_proxy, (proxy))
                        self.all_task.append(future)
                else:
                    for future in as_completed(self.all_task):
                        self.all_task.remove(future)

                        if not self.stop_flag:
                            future = self.executor.submit(self.is_valid_proxy, (proxy))
                            self.all_task.append(future)
                        break

    def stop(self):
        self.event.set()
        self.stop_flag = True

        self.executor.shutdown(wait=True)
        gc.collect()
