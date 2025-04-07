import requests
import threading
from colorama import Fore, Back, Style, init
import weakref
import logging
import gc

class Spider():
    def __init__(self, raw_proxy_queue, usable_proxy_queue=None):
        #super().__init__()
        self.raw_proxy_queue = weakref.proxy(raw_proxy_queue)
        self.usable_proxy_queue = (
            weakref.proxy(usable_proxy_queue) if usable_proxy_queue else None
        )
        self.results = []
        self.is_running = True
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

    def fetch(self, page):
        try:
            url = f"https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/all/data.txt"
            with requests.get(url=url, headers=self.headers, timeout=10) as response:
                data = response.text.split("\n")
                self.parse(data)
            logging.debug(Fore.GREEN + f"[+] proxifly/free-proxy-list done" + Fore.RESET)
            return True
        except:
            logging.debug(Fore.RED + f"[-] proxifly/free-proxy-list retry" + Fore.RESET)
            return False

    def run(self):
        for i in range(1, 2):
            while self.is_running:
                if self.fetch(i):
                    break
        gc.collect()

    def parse(self, data):
        for item in data:
            self.raw_proxy_queue.bf_put(item)
            if "socks5" in item:
                self.raw_proxy_queue.bf_put(item.replace("socks5", "socks5h"))
            if "socks4" in item:
                self.raw_proxy_queue.bf_put(item.replace("socks4", "socks4h"))

    def stop(self):
        self.is_running = False

