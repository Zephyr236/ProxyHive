from colorama import Fore
import weakref
import logging

class FlowRateLimiter:
    def __init__(self,crawler,validatormanager, raw_proxy_queue, usable_proxy_queue,per):
        self.crawler=weakref.proxy(crawler)
        self.validatormanager=weakref.proxy(validatormanager)
        self.raw_proxy_queue = weakref.proxy(raw_proxy_queue)
        self.usable_proxy_queue = weakref.proxy(usable_proxy_queue)
        self.per=per

        self.last_usable_size = 0
        self.last_raw_size = 0

        self.usable_rate = 0
        self.raw_rate=0

    def calculate_rate(self):
        current_usable_size = self.usable_proxy_queue.qsize()
        self.usable_rate = (current_usable_size - self.last_usable_size) / self.per
        self.last_usable_size = current_usable_size

        current_raw_size = self.raw_proxy_queue.qsize()
        self.raw_rate = (current_raw_size - self.last_raw_size) / self.per
        self.last_raw_size = current_raw_size

        logging.info(Fore.YELLOW + f"[!] current usable_proxy_queue: {current_usable_size}"+Fore.RESET)
        logging.info(Fore.YELLOW + f"[!] current usable_proxy_queue rate: {self.usable_rate:.2f}  items/{self.per}s"+Fore.RESET)

        logging.info(Fore.YELLOW + f"[!] current raw_proxy_queue: {current_raw_size}"+Fore.RESET)
        logging.info(Fore.YELLOW + f"[!] current raw_proxy_queue rate: {self.raw_rate:.0f}  items/{self.per}s"+Fore.RESET)

    def balance(self):
        if self.usable_rate<=0 and self.last_raw_size>10000:
            self.validatormanager.add_validator()
        elif self.usable_rate>0.30:
            self.validatormanager.remove_validator()

        if self.last_raw_size<30000:
            self.crawler.monitor_event.set()
        else:
            self.crawler.monitor_event.clear()

        if self.last_raw_size<10000:
            self.raw_proxy_queue.reset_bloom()
            self.usable_proxy_queue.reset_bloom()
            logging.info(Fore.YELLOW + "[!] All BloomFilter reset"+Fore.RESET)
            self.validatormanager.remove_validator()
