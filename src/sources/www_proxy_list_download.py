import requests
from colorama import Fore
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
        self.urls=["http","socks4","socks5"]
        self.results = []
        self.is_running = True
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

    def fetch(self, protocol):
        try:
            url = f"https://www.proxy-list.download/api/v1/get?type={protocol}"
            with requests.get(url=url, headers=self.headers, timeout=10) as response:
                if "restrict" not in response.text:
                    data=response.text.split("\r\n")
                    self.parse(data,protocol)
                else:
                    raise ValueError('restrict access')
            logging.debug(Fore.GREEN + f"[+] www_proxy_list_download {protocol} done" + Fore.RESET)
            return True
        except:
            logging.debug(Fore.RED + f"[-] www_proxy_list_download {protocol} retry" + Fore.RESET)
            return False

    def run(self):
        for i in self.urls:
            while self.is_running:
                if self.fetch(i):
                    break
        gc.collect()

    def parse(self, data,protocol):
        if protocol=="socks5":
            protocol="socks5h"
        for item in data:
            if item:
                item_proxy="{}://{}".format(protocol,item)
                self.raw_proxy_queue.bf_put(item_proxy)

    def stop(self):
        self.is_running = False
