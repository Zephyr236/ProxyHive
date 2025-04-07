from src.core import *
from src.utils import *
from colorama import Fore
import time
import sys
import logging
import requests


logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
logging.getLogger("socks").setLevel(logging.WARNING)
requests.packages.urllib3.disable_warnings()


if len(sys.argv) >= 2 and sys.argv[1] == "debug":
    logging.basicConfig(level=logging.DEBUG, format="%(message)s")
else:
    logging.basicConfig(level=logging.INFO, format="%(message)s")


if __name__ == "__main__":

    try:
        crawler = Crawler.ProxyCrawler(
            constants.raw_proxy_queue, constants.usable_proxy_queue, max_workers=3
        )
        crawler.start()
        crawler.load_verified_proxies()

        validatormanager = ValidatorManager.ValidatorManager(
            constants.raw_proxy_queue, constants.usable_proxy_queue
        )
        validatormanager.add_validator()

        flowratelimiter = FlowRateLimiter.FlowRateLimiter(
            crawler,
            validatormanager,
            constants.raw_proxy_queue,
            constants.usable_proxy_queue,
            constants.PER,
        )

        Api.start_api()

        crawlertask=CrawlerTask.CrawlerTask(constants.usable_proxy_queue,constants.crawler_task_queue)
        crawlertask.start()

        while True:
            time.sleep(constants.PER)

            flowratelimiter.calculate_rate()
            flowratelimiter.balance()

    except KeyboardInterrupt:
        logging.info(Fore.YELLOW + "[!] Stopping Crawler..." + Fore.RESET)
        crawler.stop()

        logging.info(Fore.YELLOW + "[!] Stopping Validator..." + Fore.RESET)
        validatormanager.close()

        crawler.save_list_to_file()
        crawler.join()

        logging.info(Fore.YELLOW + "[!] Stopping CrawlerTask..." + Fore.RESET)
        crawlertask.stop()
        crawlertask.join()

logging.info(Fore.GREEN + "[+] Bye~ Bye~ " + Fore.RESET)

