import requests
from colorama import Fore
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
        self.change = True
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

    def fetch(self, page):
        try:
            url = f"https://www.zdaye.com/free/{page}/"
            if self.change:
                proxy = self.usable_proxy_queue.get(timeout=10)
                proxies = {"http": proxy, "https": proxy}
                self.usable_proxy_queue.task_done()
                self.change = False

            with requests.get(
                url, proxies=proxies, headers=self.headers, timeout=10
            ) as response:
                if response.status_code == 200:
                    self.usable_proxy_queue.put(proxy)
                html = response.text
                self.parse(html)
            logging.debug(Fore.GREEN + f"[+] {url} done" + Fore.RESET)
            return True
        except:
            self.change = True
            logging.debug(Fore.RED + f"[-] {url} retry" + Fore.RESET)
            return False

    def run(self):
        for i in range(1, 13):
            while self.is_running:
                if self.fetch(i):
                    break
        gc.collect()

    def parse(self, html):
        soup = BeautifulSoup(html, "html.parser")
        table_block_div = soup.find("div", class_="abox ov")
        for table in table_block_div.find_all("table"):
            for tbody in table.find_all("tbody"):
                for tr in tbody.find_all("tr"):
                    row_data = [td.get_text() for td in tr.find_all("td")]
                    item_proxy = f"socks5://{row_data[0]}:{row_data[1]}"
                    self.raw_proxy_queue.bf_put(item_proxy)
        del soup

    def stop(self):
        self.is_running = False
