import threading
import weakref
from colorama import Fore
import logging
import datetime
import glob
from src.sources import modules
from concurrent.futures import ThreadPoolExecutor, as_completed


class ProxyCrawler(threading.Thread):
    def __init__(self, raw_proxy_queue, usable_proxy_queue, max_workers=5):
        super().__init__()
        self.stop_flag = False
        self.event = threading.Event()
        self.monitor_event = threading.Event()
        self.raw_proxy_queue = raw_proxy_queue
        self.usable_proxy_queue = usable_proxy_queue
        self.spider_refs = weakref.WeakKeyDictionary()
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(self.max_workers)
        self.all_task = []

    def load_verified_proxies(self):
        for filename in glob.glob("./valid_proxies/*proxy.txt"):
            with open(filename, "r") as f:
                content = f.read().strip()
                if content:
                    self.raw_proxy_queue.bf_put(content)

    def save_list_to_file(self):
        q = self.usable_proxy_queue

        with q.mutex:
            lst = list(q.queue.copy())

        if len(lst) == 0:
            print(Fore.RED + f"[-] Vaild is empty" + Fore.RESET)
            return

        now = datetime.datetime.now()
        formatted_time = now.strftime("%Y_%m_%d_%H_%M_%S")
        filename = formatted_time + "_proxy.txt"
        with open("./valid_proxies/" + filename, "w") as file:
            for item in lst:
                file.write(str(item) + "\n")

        logging.info(Fore.GREEN + f"[+] save {filename}" + Fore.RESET)

    def run(self):
        while not self.stop_flag:
            for i in modules:
                if self.stop_flag:
                    continue

                if not self.stop_flag:
                    spider = i.Spider(self.raw_proxy_queue, self.usable_proxy_queue)

                    if len(self.all_task) < self.max_workers:
                        if not self.stop_flag:
                            future = self.executor.submit(spider.run)
                            self.all_task.append(future)
                            self.spider_refs[future] = spider
                    else:
                        for future in as_completed(self.all_task):
                            self.all_task.remove(future)
                            spider_done=self.spider_refs.pop(future, None)
                            if spider_done is not None:
                                del spider_done

                            if not self.stop_flag:
                                future = self.executor.submit(spider.run)
                                self.all_task.append(future)
                                self.spider_refs[future] = spider
                            break
                """
                spider=i.Spider(self.raw_proxy_queue, self.usable_proxy_queue)
                self.spiders.append(spider)
                spider.start()
                """
            for future in as_completed(self.all_task):
                self.all_task.remove(future)

            if not self.monitor_event.is_set():
                logging.info(Fore.YELLOW + f"[!] Crawler paused"+Fore.RESET)
            self.monitor_event.wait()
            if self.monitor_event.is_set() and not self.event.is_set():
                logging.info(Fore.YELLOW + f"[!] Crawler running"+Fore.RESET)

    def stop(self):
        self.stop_flag = True
        self.event.set()
        self.monitor_event.set()
        for spider in list(self.spider_refs.values()):
            spider.stop()
        self.executor.shutdown(wait=True)
