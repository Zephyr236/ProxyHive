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
        self.results = []
        self.is_running = True
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

    def fetch(self, page):
        try:
            url = f"https://proxylist.geonode.com/api/proxy-list?limit=500&page={page}&sort_by=lastChecked&sort_type=desc"
            with requests.get(url=url, timeout=10) as response:
                proxy_json = response.json()
                self.parse(proxy_json["data"])
            logging.debug(Fore.GREEN + f"[+] proxylist.geonode.com {page} done" + Fore.RESET)
            return True
        except:
            logging.debug(Fore.RED + f"[-] proxylist.geonode.com {page} retry" + Fore.RESET)
            return False

    def run(self):
        for i in range(1, 18):
            while self.is_running:
                if self.fetch(i):
                    break
        gc.collect()

    def parse(self, data):
        for item in data:
            proxy_item = "{}://{}:{}".format(
                item["protocols"][0], item["ip"], item["port"]
            )
            proxy_item = proxy_item.lower()
            if "socks5" in proxy_item:
                self.raw_proxy_queue.bf_put(proxy_item.replace("socks5", "socks5h"))

            if "socks4" in proxy_item:
                self.raw_proxy_queue.bf_put(proxy_item.replace("socks4", "socks4h"))

    def stop(self):
        self.is_running = False

