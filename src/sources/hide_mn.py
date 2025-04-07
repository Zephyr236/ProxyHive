import requests
import threading
from colorama import Fore, Back, Style, init
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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
        self.stop_event = threading.Event()

    def fetch(self, page):
        if self.stop_event.is_set():
            return

        while not self.stop_event.is_set():
            try:
                url = f"http://hide.mn/en/proxy-list/?start={64*page}#list"
                proxy = self.usable_proxy_queue.get(timeout=10)
                proxies = {
                'http': proxy,
                'https': proxy
                }
                self.usable_proxy_queue.task_done()
                with requests.get(url, headers=self.headers,verify=False,proxies=proxies,timeout=10) as response:
                    if response.status_code==200:
                        self.usable_proxy_queue.put(proxy)
                    html=response.text
                    self.parse(html)
                logging.debug(Fore.GREEN + f"[+] {url} done"+Fore.RESET)
                break
            except Exception as e:
                logging.debug(Fore.RED + f"[-] {url} retry"+Fore.RESET)
                #print(Fore.RED + f"[-] Error occurred: {e}"+Fore.RESET)
                pass

    def run(self):
        with ThreadPoolExecutor(max_workers=5) as executor:
            try:
                _ = executor.map(self.fetch, range(0, 190))

            except:
                pass
        self.stop()
        gc.collect()

    def parse(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        table_block_div = soup.find('div', class_='table_block')
        for table in table_block_div.find_all('table'):
            for tbody in table.find_all('tbody'):
                for tr in tbody.find_all('tr'):
                    row_data = [td.get_text(strip=True) for td in tr.find_all('td')]
                    
                    if row_data:
                        proxy_item="{}://{}:{}".format(row_data[4].split(",")[0],row_data[0],row_data[1])
                        proxy_item=proxy_item.lower()
                        #print(proxy_item)
                        if "socks5" in proxy_item:
                            self.raw_proxy_queue.bf_put(proxy_item.replace("socks5","socks5h"))

                        if "socks4" in proxy_item:  
                            self.raw_proxy_queue.bf_put(proxy_item.replace("socks4","socks4h"))
                        #print(proxy_item)
                        self.raw_proxy_queue.bf_put(proxy_item)
        del soup

    def stop(self):
        self.is_running = False
        self.stop_event.set()

