import json
import logging
import re
from time import sleep
from urllib.parse import urljoin

import requests
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


def get_cleaned_comments(comments: list) -> list:
    cleaned_comments = [
        comment.replace("\n", " ").replace('"', "'") for comment in comments
    ]
    return cleaned_comments


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    start_page = 1
    end_page = 1
    #! TODO добавить обработку последней страницы
    all_books = []
    for page in range(start_page, end_page + 1):
        BOOKS_FANTASY_URL = urljoin("https://tululu.org/l55/", str(page))
        response = fetch_book_response(BOOKS_FANTASY_URL)

        soup = BeautifulSoup(response.text, "lxml")
        cart_book_selector = "div.bookimage"
        carts_books = soup.select(cart_book_selector)

        for cart in carts_books:
            retries = 3
            attempt = 0
            while attempt < retries:
                try:
                    link_selector = "a"
                    part_link = cart.select_one(link_selector)["href"]
                    link = urljoin(BASE_URL, part_link)
                    response = fetch_book_response(link)
                    title, author, image_path, comments, genres = parse_book_page(
                        response
                    )
                    # Убираем из комментариев \n
                    cleaned_comments = get_cleaned_comments(comments)
                    book_id = get_book_id(part_link)
                    # Скачиваем книгу
                    download_book_url = "https://tululu.org/txt.php"
                    book = fetch_book_response(
                        url=download_book_url, params={"id": book_id}
                    )

                    if book.content:
                        save_to_file(book.content, "Books", f"{book_id}. {title}")
                    else:
                        break

                    # Скачиваем изображение
                    cover_url = urljoin(response.url, image_path)
                    image = fetch_book_response(url=cover_url)
                    _, img_ext = tuple(image_path.split("."))
                    save_to_file(image.content, "Image", title, extension=img_ext)

                    # Создаем json файл
                    book_path = f"Books/{title}.txt"
                    image_src = f"Image/{title}.{img_ext}"
                    all_books.append(
                        {
                            "title": title,
                            "author": author,
                            "image_src": image_src,
                            "book_path": book_path,
                            "comments": cleaned_comments,
                            "genres": genres,
                        }
                    )
                    break
                except requests.HTTPError:
                    logging.info(f"Не удалось загрузить книгу с id = {str(book_id)}")
                    attempt += 1
                    sleep(1)
                    continue
                except requests.ConnectionError:
                    logging.info("Не удалось подключиться к серверу")
                    attempt += 1
                    sleep(1)
                    continue

    books_json = json.dumps(all_books, ensure_ascii=False, indent=3)

    with open("books.json", "w") as my_file:
        my_file.write(books_json)
