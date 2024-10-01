import requests


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError()


def fetch_book_response(book_id):
    url = f"https://tululu.org/b{book_id}/"
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    return response


def fetch_book_image(cover_path):
    cover_url = f"https://tululu.org{cover_path}"
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
