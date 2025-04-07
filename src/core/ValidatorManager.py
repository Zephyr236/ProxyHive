from src.utils.Validator import ProxyValidator
from colorama import Fore
import logging


class ValidatorManager:
    def __init__(self, raw_proxy_queue, usable_proxy_queue):
        super().__init__()
        self.raw_proxy_queue = raw_proxy_queue
        self.usable_proxy_queue = usable_proxy_queue
        self.all_task = []
        self.THREAD_ID = 1
        self.validator_dict = {}

    def add_validator(self):
        validator = ProxyValidator(
            self.raw_proxy_queue, self.usable_proxy_queue, max_workers=50
        )
        self.validator_dict[self.THREAD_ID] = validator
        validator.start()
        logging.info(Fore.YELLOW + f"[!] Running Validator{self.THREAD_ID}" + Fore.RESET)
        self.THREAD_ID = self.THREAD_ID + 1

    def remove_validator(self):
        if self.THREAD_ID > 2:
            self.THREAD_ID = self.THREAD_ID - 1
            validator = self.validator_dict.pop(self.THREAD_ID, None)
            if validator is None:
                print(
                    Fore.YELLOW + f"[!] Removed Validator{self.THREAD_ID}" + Fore.RESET
                )
            else:
                validator.stop()
                del validator
                print(
                    Fore.YELLOW + f"[!] Removed Validator{self.THREAD_ID}" + Fore.RESET
                )

    def close(self):
        for key in list(self.validator_dict.keys()):
            validator = self.validator_dict.pop(key, None)
            if validator is not None:
                validator.stop()
                validator.join()
                
                logging.info(Fore.YELLOW + f"[!] Removed Validator{key}" + Fore.RESET)
        self.validator_dict.clear()

