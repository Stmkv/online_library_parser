import argparse
import logging
from time import sleep
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

from parser_response_tools import (
    fetch_book_response,
)
from save_book_tools import save_to_file

logging.basicConfig(level=logging.INFO)


def parse_book_page(response):
    soup = BeautifulSoup(response.text, "lxml")
    title_and_author = soup.find(id="content").find("h1").text
    title, author = tuple(title_and_author.split(" \xa0 :: \xa0 "))
    image_path = soup.find(class_="bookimage").find("img")["src"]
    comments = soup.find_all("div", class_="texts")
    all_comments = [comment.find("span").text for comment in comments]
    genre = soup.find_all("span", class_="d_book")
    all_genres = [genre.text for genre in genre]
    return sanitize_filename(title), author, image_path, all_comments, all_genres


def get_range_book_id():
    parser = argparse.ArgumentParser(description="Скачивает выбранные книги с тулулу")
    parser.add_argument(
        "left_border",
        type=int,
        default=0,
    )
    parser.add_argument(
        "right_border",
        type=int,
        default=10,
    )
    args = parser.parse_args()
    return args.left_border, args.right_border


if __name__ == "__main__":
    left_border, right_border = get_range_book_id()
    for book_id in range(left_border, right_border + 1):
        retries = 3
        attempt = 0
        while attempt < retries:
            try:
                book_url = f"https://tululu.org/b{book_id}/"
                response = fetch_book_response(book_url)

                title, author, image_path, comments, genres = parse_book_page(response)

                download_book_url = "https://tululu.org/txt.php"
                book = fetch_book_response(
                    url=download_book_url, params={"id": book_id}
                )

                cover_url = urljoin(response.url, image_path)
                image = fetch_book_response(url=cover_url)

                _, img_ext = tuple(image_path.split("."))

                save_to_file(book.content, "Books", f"{book_id}. {title}")
                save_to_file(image.content, "Image", title, extension=img_ext)
                save_to_file(comments, "Comments", title)
                save_to_file(genres, "Genres", title)
                break
            except requests.HTTPError:
                logging.info("Не удалось загрузить книгу с id = " + str(book_id))
                sleep(1)
                attempt += 1
                continue
            except requests.ConnectionError:
                logging.info("Не удалось подключиться к серверу")
                sleep(1)
                attempt += 1
                continue
