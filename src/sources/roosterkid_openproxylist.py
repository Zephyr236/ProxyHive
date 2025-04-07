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
        self.urls = [
            [
                "https://api.allorigins.win/get?url=https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4.txt",
                "socks4",
            ],
            [
                "https://api.allorigins.win/get?url=https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5.txt",
                "socks5h",
            ],
            [
                "https://api.allorigins.win/get?url=https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS.txt",
                "https",
            ],
        ]

    def fetch(self, url):
        try:
            with requests.get(url=url[0], headers=self.headers, timeout=10) as response:
                proxy_json = response.json()
                self.parse(proxy_json["contents"], url[1])
            logging.debug(Fore.GREEN + f"[+] api.allorigins.win {url[1]} done" + Fore.RESET)
            return True
        except:
            logging.debug(Fore.RED + f"[-] api.allorigins.win {url[1]} retry" + Fore.RESET)
            return False

    def run(self):
        for i in self.urls:
            while self.is_running:
                if self.fetch(i):
                    break
        gc.collect()

    def parse(self, data, protocol):
        raw_data = data.split("\n")
        raw_data = raw_data[12:-1]
        for item in raw_data:
            data = item.split(" ")
            proxy_item = "{}://{}".format(protocol, data[1])
            self.raw_proxy_queue.bf_put(proxy_item)
            proxy_item = "{}://{}".format(protocol, data[1])
            self.raw_proxy_queue.bf_put(proxy_item)

    def stop(self):
        self.is_running = False

