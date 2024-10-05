import json
import logging
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from parser_response_tools import fetch_book_response
from save_book_tools import save_to_file
from tululu import parse_book_page

BASE_URL = "https://tululu.org/"
logging.basicConfig(level=logging.INFO)


def get_book_id(link: str) -> str:
    math = re.search(r"\d+", link)
    if math:
        book_id = math.group()
    return book_id


start_page = 1
end_page = 1
#! TODO добавить обработку последней страницы
json_books = []
for _ in range(start_page, end_page + 1):
    BOOKS_FANTASY_URL = urljoin("https://tululu.org/l55/", str(start_page))
    response = fetch_book_response(BOOKS_FANTASY_URL)

    soup = BeautifulSoup(response.text, "lxml")
    carts_books = soup.find_all("div", class_="bookimage")

    retries = 3
    attempt = 0
    for cart in carts_books:
        while attempt < retries:
            try:
                part_link = cart.find("a")["href"]
                link = urljoin(BASE_URL, part_link)
                response = fetch_book_response(link)
                title, author, image_path, comments, genres = parse_book_page(response)
                # Убираем из комментариев \n
                feedbak = []
                for comment in comments:
                    if r"\n" in comment:
                        comment = comment.replace(r"\n", "")
                    feedbak.append(comment)

                book_id = get_book_id(part_link)
                # Скачиваем книгу
                download_book_url = "https://tululu.org/txt.php"
                book = fetch_book_response(
                    url=download_book_url, params={"id": book_id}
                )
                # save_to_file(book.content, "Books", f"{book_id}. {title}")
                # Скачиваем изображение
                cover_url = urljoin(response.url, image_path)
                image = fetch_book_response(url=cover_url)
                _, img_ext = tuple(image_path.split("."))
                # save_to_file(image.content, "Image", title, extension=img_ext)

                # Создаем json файл
                book_path = f"Books/{title}.{img_ext}"
                image_src = f"Image/{title}.{img_ext}"
                json_books.append(
                    {
                        "title": title,
                        "author": author,
                        "image_src": image_src,
                        "book_path" "comments": feedbak,
                        "genres": genres,
                    }
                )
                break
            except requests.HTTPError:
                logging.info(f"Не удалось загрузить книгу с id = {str(book_id)}")
                attempt += 1
                continue
            except requests.ConnectionError:
                logging.info("Не удалось подключиться к серверу")
                attempt += 1
                continue

books_json = json.dumps(json_books, ensure_ascii=False, indent=3)

with open("books.json", "w") as my_file:
    my_file.write(books_json)
