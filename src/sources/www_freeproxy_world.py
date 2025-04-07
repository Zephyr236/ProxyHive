import requests
from colorama import Fore
import threading
from bs4 import BeautifulSoup
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
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
        self.stop_event = threading.Event()

    def fetch(self, page):
        if self.stop_event.is_set():
            return
        while True and not self.stop_event.is_set():
            try:
                url = f"https://www.freeproxy.world/?type=&anonymity=&country=&speed=&port=&page={page}"
                with requests.get(
                    url=url, headers=self.headers, timeout=10
                ) as response:
                    html = response.text
                    self.parse(html)
                logging.debug(
                    Fore.GREEN
                    + f"[+] www_freeproxy_world page {page} done"
                    + Fore.RESET
                )
                break
            except:
                logging.debug(
                    Fore.RED + f"[-] www_freeproxy_world page {page} retry" + Fore.RESET
                )
                pass

    def run(self):
        with ThreadPoolExecutor(max_workers=5) as executor:
            try:
                _ = executor.map(self.fetch, range(1, 751))
            except Exception as e:
                logging.debug(Fore.RED + f"[-] Error occurred: {e}" + Fore.RESET)
        self.stop()
        gc.collect()

    def parse(self, html):
        soup = BeautifulSoup(html, "html.parser")
        table_block_div = soup.find("div", class_="proxy-table")
        for table in table_block_div.find_all("table"):
            for tbody in table.find_all("tbody"):
                for tr in tbody.find_all("tr"):
                    raw_data = [td.get_text(strip=True) for td in tr.find_all("td")]
                    if len(raw_data) > 1:
                        if len(raw_data[5]) <= 6:
                            item_proxy = "{}://{}:{}".format(
                                raw_data[5].replace("socks5", "socks5h"),
                                raw_data[0],
                                raw_data[1],
                            )
                            self.raw_proxy_queue.bf_put(item_proxy)
                        else:
                            if "socks5" in raw_data[5]:
                                item_proxy = "{}://{}:{}".format(
                                    "socks5h", raw_data[0], raw_data[1]
                                )
                                self.raw_proxy_queue.bf_put(item_proxy)

                            if "socks4" in raw_data[5]:
                                item_proxy = "{}://{}:{}".format(
                                    "socks4", raw_data[0], raw_data[1]
                                )
                                self.raw_proxy_queue.bf_put(item_proxy)

                            if "http" in raw_data[5] and "https" not in raw_data[5]:
                                item_proxy = "{}://{}:{}".format(
                                    "http", raw_data[0], raw_data[1]
                                )
                                self.raw_proxy_queue.bf_put(item_proxy)

                            if "https" in raw_data[5]:
                                item_proxy = "{}://{}:{}".format(
                                    "https", raw_data[0], raw_data[1]
                                )
                                self.raw_proxy_queue.bf_put(item_proxy)
        del soup

    def stop(self):
        self.is_running = False
        self.stop_event.set()


