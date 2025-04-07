import requests
import threading
from colorama import Fore, Back, Style, init
from bs4 import BeautifulSoup
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

    def fetch(self):
        try:
            url = f"https://api.allorigins.win/get?url=https://free-proxy-list.net/"
            with requests.get(url=url, headers=self.headers, timeout=10) as response:
                html = response.json()["contents"]
                self.parse(html)
            logging.debug(Fore.GREEN + f"[+] free_proxy_list_net done" + Fore.RESET)
            return True
        except Exception as e:
            #logging.debug(Fore.RED + "[-] error:", e, Fore.RESET)
            logging.debug(Fore.RED + f"[-] free_proxy_list_net retry" + Fore.RESET)
            return False

    def run(self):
        for _ in range(1, 2):
            while self.is_running:
                if self.fetch():
                    break
        gc.collect()

    def parse(self, html):
        soup = BeautifulSoup(html, "html.parser")
        table_block_div = soup.find("div", class_="table-responsive fpl-list")
        for table in table_block_div.find_all("table"):
            for tbody in table.find_all("tbody"):
                for tr in tbody.find_all("tr"):
                    row_data = [td.get_text(strip=True) for td in tr.find_all("td")]
                    if row_data:
                        item_proxy = "{}://{}:{}".format(
                            "http", row_data[0], row_data[1]
                        )
                        self.raw_proxy_queue.bf_put(item_proxy)
                        item_proxy = "{}://{}:{}".format(
                            "socks5h", row_data[0], row_data[1]
                        )
                        self.raw_proxy_queue.bf_put(item_proxy)
                        item_proxy = "{}://{}:{}".format(
                            "socks4", row_data[0], row_data[1]
                        )
                        self.raw_proxy_queue.bf_put(item_proxy)
                        item_proxy = "{}://{}:{}".format(
                            "https", row_data[0], row_data[1]
                        )
                        self.raw_proxy_queue.bf_put(item_proxy)
        del soup

    def stop(self):
        self.is_running = False
