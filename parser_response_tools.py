import logging
import time
from urllib.parse import urljoin

import requests

logging.basicConfig(level=logging.INFO)


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError()


def fetch_book_response(book_id, retries=3):
    url = f"https://tululu.org/b{book_id}/"
    response = requests.get(url, timeout=1)
    response.raise_for_status()
    check_for_redirect(response)
    return response


def fetch_content_book(
    base_url=None,
    book_id=None,
    cover_path=None,
):
    if book_id is not None:
        url = "https://tululu.org/txt.php"
        response = requests.get(url, params={"id": book_id})
    else:
        cover_url = urljoin(base_url, cover_path)
        response = requests.get(url=cover_url)
    response.raise_for_status()
    check_for_redirect(response)
    return response.content
