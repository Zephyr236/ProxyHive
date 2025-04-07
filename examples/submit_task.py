import requests

url = "http://127.0.0.1:5000/submit"

data = {
    "url": "http://ipconfig.me/all",
    "method": "get",
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
}

response = requests.post(url, json=data)
print(response.text)

data = {
    "url": "https://httpbin.org/post",
    "method": "post",
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    },
    "data":{"key": "value"}
}

response = requests.post(url, json=data)
print(response.text)