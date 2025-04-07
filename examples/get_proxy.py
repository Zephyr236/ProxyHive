import requests


def get_proxy():
    return requests.get("http://127.0.0.1:5000/get").json()["proxy"]


def spider(url):
    change = True
    retry_count = 10
    while retry_count > 0:
        try:
            if change:
                proxy = get_proxy()
                proxies = {"http": proxy, "https": proxy}
                change = False
            html = requests.get(url=url, proxies=proxies, timeout=10)
            return html
        except Exception:
            change = True
            retry_count -= 1
            print("retry")

    return None


response = spider("http://ipconfig.info")
if response:
    print(response.text)
