import requests
from colorama import Fore
import logging
import weakref
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
            url = f"https://sockslist.us/Raw"
            with requests.get(url=url, headers=self.headers, timeout=10) as response:
                data = response.text.split("\n")
                self.parse(data)
            logging.debug(Fore.GREEN + f"[+] sockslist_us done {page} done" + Fore.RESET)
            return True
        except:
            logging.debug(Fore.RED + f"[-] sockslist_us done {page} retry" + Fore.RESET)
            return False

    def run(self):
        for i in range(1, 2):
            while self.is_running:
                if self.fetch(i):
                    break
        gc.collect()

    def parse(self, data):
        for item in data:
            if item:
                proxy_item = "socks5://{}".format(item)
                self.raw_proxy_queue.bf_put(proxy_item)
                proxy_item = "socks5h://{}".format(item)
                self.raw_proxy_queue.bf_put(proxy_item)

    def stop(self):
        self.is_running = False

