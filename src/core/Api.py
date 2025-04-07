from flask import Flask, jsonify, request, Response
from src.utils import constants, WebProxy
import threading
import logging
import queue
import weakref
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from werkzeug.serving import WSGIRequestHandler
from werkzeug.exceptions import BadRequest
from urllib.parse import unquote
import uuid

app = Flask(__name__)
usable_proxy_queue_ref = weakref.proxy(constants.usable_proxy_queue)
crawler_task_queue_ref = weakref.proxy(constants.crawler_task_queue)


@app.route("/submit", methods=["POST"])
def submit():
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 415

        data = request.get_json(force=False, silent=False, cache=False)

        url = data.get("url", None)
        if url is None:
            return jsonify({"error": "Missing required url"}), 400

        method = data.get("method", None)
        if not (method.lower() == "get" or method.lower() == "post"):
            return jsonify({"error": "Missing required method"}), 400

        headers = data.get("headers", None)
        if headers is None:
            return jsonify({"error": "Missing required headers"}), 400
        

        unique_id = uuid.uuid4()
        task = {"file_id": unique_id, "task": data}
        crawler_task_queue_ref.put(task)

        del unique_id
        return jsonify(task), 200

    except BadRequest:
        return jsonify({"error": "Invalid JSON format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/proxy", methods=["GET", "POST"])
def proxy():

    url = unquote(request.args.get("url"))
    if not url:
        return jsonify({"error": "Missing URL parameter"}), 400

    proxies = []
    for _ in range(10):
        try:
            proxy = usable_proxy_queue_ref.get_nowait()
            proxies.append(proxy)
        except queue.Empty:
            break
    for _ in proxies:
        usable_proxy_queue_ref.task_done()

    if not proxies:
        return jsonify({"error": "No available proxies"}), 503

    webproxy = WebProxy.WebProxy(
        url,
        proxies,
        request.method,
        request.headers,
        request.get_data(),
        request.cookies,
        usable_proxy_queue_ref,
    )
    result = webproxy.proxy()
    del proxies
    del webproxy
    return result


@app.route("/get")
def get_proxy():
    try:
        proxy = usable_proxy_queue_ref.get(block=True, timeout=5)
        if proxy:
            usable_proxy_queue_ref.task_done()
        return jsonify({"proxy": proxy})
    except queue.Empty:
        return jsonify({"error": "No proxies available"}), 404


def run_api():
    log = logging.getLogger("werkzeug")
    log.disabled = True
    WSGIRequestHandler.log_request = lambda *args, **kwargs: None

    app.run(host="0.0.0.0", port=5000, threaded=True)


def start_api():
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
