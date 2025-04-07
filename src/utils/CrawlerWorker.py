from colorama import Fore
import requests
import logging
from src.sources import modules


class CrawlerWorker():
    def __init__(self, usable_proxy_queue,crawler_task_queue,task,file_id):
        self.usable_proxy_queue=usable_proxy_queue
        self.crawler_task_queue=crawler_task_queue

        self.url=task.get("url",None)
        self.method=task.get("method",None)
        self.headers=task.get("headers",None)
        self.data=task.get("data",None)
        self.file_id=file_id
        self.json_data=task



    def run(self):
        for _ in range(0,10):
            try:
                proxy = self.usable_proxy_queue.get(timeout=10)
                proxies = {
                'http': proxy,
                'https': proxy
                }
                self.usable_proxy_queue.task_done()
                with requests.request(url=self.url,method=self.method,data=self.data, headers=self.headers,verify=False,proxies=proxies,timeout=10) as response:
                    if response.status_code==200:
                        self.usable_proxy_queue.put(proxy)
                    with open("./task_results/"+str(self.file_id), 'wb') as file: 
                        file.write(response.content)

                logging.info(Fore.GREEN + f"[+] {self.file_id} done" + Fore.RESET)
                return True
            except Exception as e:
                logging.debug(Fore.GREEN + f"[-] {self.file_id} error {e}" + Fore.RESET)
                continue
        try:
            with open("./task_results/"+str(self.file_id), 'w') as file: 
                file.write(str(self.json_data))
            logging.debug(Fore.RED + f"[+] {self.file_id} fail" + Fore.RESET)
        except Exception as e:
            logging.debug(Fore.RED + f"[-] {self.file_id} error {e}" + Fore.RESET)
        return False