import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from parser_response_tools import fetch_book_response
from save_book_tools import save_to_file
from tululu import parse_book_page

BASE_URL = "https://tululu.org/"


def get_book_id(link: str) -> str:
    math = re.search(r"\d+", link)
    if math:
        book_id = math.group()
    return book_id


start_page = 1
end_page = 1
#! TODO добавить обработку последней страницы
while start_page <= end_page:
    BOOKS_FANTASY_URL = urljoin("https://tululu.org/l55/", str(start_page))
    response = fetch_book_response(BOOKS_FANTASY_URL)

    soup = BeautifulSoup(response.text, "lxml")
    carts_books = soup.find_all("div", class_="bookimage")

    for id_book in carts_books:
        part_link = id_book.find("a")["href"]
        link = urljoin(BASE_URL, part_link)
        response = fetch_book_response(link)
        title, author, image_path, comments, genres = parse_book_page(response)

        book_id = get_book_id(part_link)
        # Скачиваем книгу
        download_book_url = "https://tululu.org/txt.php"
        book = fetch_book_response(url=download_book_url, params={"id": book_id})
        # save_to_file(book.content, "Books", f"{book_id}. {title}")
        # Скачиваем изображение
        cover_url = urljoin(response.url, image_path)
        image = fetch_book_response(url=cover_url)
        _, img_ext = tuple(image_path.split("."))
        save_to_file(image.content, "Image", title, extension=img_ext)
    start_page += 1
