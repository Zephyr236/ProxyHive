from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, jsonify, request, Response
import threading
import requests
import logging
from colorama import Fore

class WebProxy:
    def __init__(self, url, proxies, method, headers, data, cookies,usable_proxy_queue_ref):
        self.url=url
        self.proxies = proxies
        self.method = method
        self.headers = headers
        self.data = data
        self.cookies = cookies
        self.usable_proxy_queue_ref=usable_proxy_queue_ref

        self.stop_event = threading.Event()


    def proxy(self):
        futures = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            for proxy in self.proxies:
                future = executor.submit(
                    self.make_request,
                    self.url,
                    proxy,
                    self.method,
                    self.headers,
                    self.data,
                    self.cookies,
                )
                futures.append(future)

            try:
                for future in as_completed(futures, timeout=15):
                    if self.stop_event.is_set():
                        future.cancel()
                        continue

                    result = future.result()
                    if result:
                        self.stop_event.set()
                        for p in self.proxies:
                            if p != result["proxy"]:
                                self.usable_proxy_queue_ref.put(p)
                        return Response(
                            result["content"],
                            status=result["status_code"],
                            headers=result["headers"],
                        )
            except Exception as e:
                logging.debug(Fore.RED + f"api error: {str(e)}")

            return jsonify({"error": "All proxies failed"}), 500

    def make_request(self,url, proxy, method, headers, data, cookies):
        if self.stop_event.is_set():
            return None

        try:
            with requests.request(
                method=method,
                url=url,
                headers={k: v for k, v in headers if k.lower() != "host"},
                data=data,
                cookies=cookies,
                proxies={"http": proxy, "https": proxy},
                timeout=10,
                allow_redirects=False,
                stream=False,
            ) as response:

                headers = {
                    k: v
                    for k, v in response.headers.items()
                    if k.lower() not in ["transfer-encoding", "connection"]
                }
                headers["Content-Length"] = str(len(response.content))

                return {
                    "proxy": proxy,
                    "content": response.content,
                    "status_code": response.status_code,
                    "headers": headers,
                }

        except Exception as e:
            logging.debug(Fore.RED + f"[-] {proxy} fail: {str(e)}"+Fore.RESET)
            return None
        