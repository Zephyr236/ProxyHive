import requests
from colorama import Fore, Back, Style, init
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import weakref
import threading
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
        self.headers =  {
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br, zstd",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Connection": "keep-alive",
                    "Content-Type": "text/plain;charset=UTF-8",
                    "Host": "proxydb.net",
                    "Origin": "https://proxydb.net",
                    "Referer": "https://proxydb.net/?offset=30",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-origin",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
                    "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"'
                }
        self.stop_event = threading.Event()

    def fetch(self, page):
        if self.stop_event.is_set():
            return
        
        data = {
            "protocols": [],
            "anonlvls": [],
            "offset": page*30
        }

        while not self.stop_event.is_set():
            try:
                url = "https://proxydb.net/list"
                with requests.post(
                    url,
                    headers=self.headers,
                    json=data,
                    timeout=10
                ) as response:
                    data=response.json()["proxies"]
                    self.parse(data)
                logging.debug(
                    Fore.GREEN
                    + f"[+] proxydb_net page {page} done"
                    + Fore.RESET
                )
                break
            except:
                logging.debug(
                    Fore.RED + f"[-] proxydb_net page {page} retry" + Fore.RESET
                )
                pass

    def run(self):
        with ThreadPoolExecutor(max_workers=5) as executor:
            try:
                _ = executor.map(self.fetch, range(0, 461))
            except Exception as e:
                logging.debug(Fore.RED + f"[-] Error occurred: {e}" + Fore.RESET)
        self.stop()
        gc.collect()
        

    def parse(self, data):
        for item in data:
            item_proxy="{}://{}:{}".format(item["type"].replace("socks5","socks5h"),item["ip"],item["port"])
            self.raw_proxy_queue.bf_put(item_proxy)

    def stop(self):
        self.is_running = False
        self.stop_event.set()

