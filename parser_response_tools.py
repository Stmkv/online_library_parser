import logging
import time
from urllib.parse import urljoin

import requests

logging.basicConfig(level=logging.INFO)


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError()


def fetch_book_response(url, params=None):
    response = requests.get(url, params)
    response.raise_for_status()
    check_for_redirect(response)
    return response
