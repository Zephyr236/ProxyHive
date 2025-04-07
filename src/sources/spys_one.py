import requests
from colorama import Fore
import logging
from bs4 import BeautifulSoup
import weakref
import gc

class Spider():
    def __init__(self, raw_proxy_queue, usable_proxy_queue=None):
        #super().__init__()
        self.raw_proxy_queue = weakref.proxy(raw_proxy_queue)
        self.usable_proxy_queue = (
            weakref.proxy(usable_proxy_queue) if usable_proxy_queue else None
        )
        self.urls = [
            "FR",
            "US",
            "RU",
            "HK",
            "JP",
            "BR",
            "SG",
            "ID",
            "FI",
            "TH",
            "CO",
            "MX",
        ]
        self.results = []
        self.is_running = True
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

    def fetch(self, country):
        try:
            url = f"https://api.allorigins.win/get?url=https://spys.one/free-proxy-list/{country}"
            with requests.get(url=url, headers=self.headers, timeout=10) as response:
                html = response.json()["contents"]
                self.parse(html)
            logging.debug(Fore.GREEN + f"[+] spys_one {country} done" + Fore.RESET)
            return True
        except:
            logging.debug(Fore.RED + f"[-] spys_one {country} retry" + Fore.RESET)
            return False

    def run(self):
        for i in self.urls:
            while self.is_running:
                if self.fetch(i):
                    break
        gc.collect()

    def parse(self, html):
        soup = BeautifulSoup(html, "html.parser")

        tr_list = soup.find_all("tr", class_=["spy1xx", "spy1x"])
        for tr in tr_list:
            data = str(tr.text).lower()
            if "https" in data:
                ip = data.split("https")[0]
                item_proxy = f"https://{ip}"
                self.raw_proxy_queue.bf_put(item_proxy)
                continue

            if "http" in data:
                ip = data.split("http")[0]
                item_proxy = f"http://{ip}"
                self.raw_proxy_queue.bf_put(item_proxy)
                continue

            if "socks5" in data:
                ip = data.split("socks5")[0]
                item_proxy = f"socks5h://{ip}"
                self.raw_proxy_queue.bf_put(item_proxy)
                continue

            if "socks4" in data:
                ip = data.split("socks4")[0]
                item_proxy = f"socks4://{ip}"
                self.raw_proxy_queue.bf_put(item_proxy)
                continue
        del soup

    def stop(self):
        self.is_running = False

