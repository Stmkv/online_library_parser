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
    waiting_time = 0
    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(url, timeout=1)
            response.raise_for_status()
            check_for_redirect(response)
            return response
        except requests.exceptions:
            logging.info(f"Attempt {attempt} failed, retrying")
        attempt += 1
        time.sleep(waiting_time)
        waiting_time += 1


def fetch_book_image(cover_path):
    cover_url = urljoin("https://tululu.org/", cover_path)
    response = requests.get(url=cover_url)
    response.raise_for_status()
    check_for_redirect(response)
    return response.content


def get_book(book_id):
    url = "https://tululu.org/txt.php"
    response = requests.get(url, params={"id": book_id})
    response.raise_for_status()
    check_for_redirect(response)
    return response.content
