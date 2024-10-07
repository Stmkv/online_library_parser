import argparse
import json
import logging
import os
import re
import sys
from time import sleep
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from parser_response_tools import fetch_book_response
from save_book_tools import save_to_file
from tululu import parse_book_page


def get_book_url(cart) -> str:
    link_selector = "a"
    book_url = cart.select_one(link_selector)["href"]
    link = urljoin(base_url, book_url)
    return link


def save_books_to_json_file(user_folder, books):
    os.makedirs(user_folder, exist_ok=True)
    with open(os.path.join(user_folder, "books.json"), "w") as file:
        json.dump(books, file, ensure_ascii=False, indent=3)


def get_cleaned_book_id(link: str) -> str:
    math = re.search(r"\d+", link)
    if math:
        book_id = math.group()
    else:
        logging.info(f"Не удалось получить id книги из ссылки {link}")
    return book_id


def get_cleaned_comments(comments: list) -> list:
    cleaned_comments = [
        comment.replace("\n", " ").replace('"', "'") for comment in comments
    ]
    return cleaned_comments


def get_settings_parser():
    parser = argparse.ArgumentParser(description="Скачивает книги с сайта tululu.org")
    parser.add_argument(
        "--start_page",
        type=int,
        default=1,
        help="номер страницы, с которой начать скачивание",
    )
    parser.add_argument(
        "--end_page",
        type=int,
        default=702,
        help="номер страницы, которой закончить скачивание",
    )
    parser.add_argument(
        "--skip_txt", action="store_true", default=False, help="не скачивать книги"
    )
    parser.add_argument(
        "--skip_img", action="store_true", default=False, help="не скачивать обложки"
    )
    parser.add_argument(
        "--dest_folder",
        type=str,
        default="books",
        help="путь к каталогу с книгами, обложками, JSON",
    )
    args = parser.parse_args()
    return (
        args.start_page,
        args.end_page,
        args.skip_txt,
        args.skip_img,
        args.dest_folder,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_page, end_page, skip_txt, skip_img, dest_folder = get_settings_parser()
    base_url = "https://tululu.org/"

    all_books = []
    for page in range(start_page, end_page + 1):
        books_fantasy_url = urljoin("https://tululu.org/l55/", str(page))
        try:
            response = fetch_book_response(books_fantasy_url)
        except requests.HTTPError:
            logging.error("Заданная страница не существует")
            continue
        except requests.ConnectionError:
            logging.info("Не удалось подключиться к серверу")
            continue
        soup = BeautifulSoup(response.text, "lxml")
        cart_book_selector = "div.bookimage"
        carts_books = soup.select(cart_book_selector)

        for cart in carts_books:
            retries = 3
            attempt = 0
            while attempt < retries:
                try:
                    book_url = get_book_url(cart)
                    response = fetch_book_response(book_url)
                    title, author, image_path, comments, genres = parse_book_page(
                        response
                    )

                    cleaned_comments = get_cleaned_comments(comments)
                    cleaned_book_id = get_cleaned_book_id(book_url)

                    if not skip_txt:
                        download_book_url = "https://tululu.org/txt.php"
                        book = fetch_book_response(
                            url=download_book_url, params={"id": cleaned_book_id}
                        )
                        if book.content:
                            save_to_file(
                                content=book.content,
                                directory=dest_folder,
                                name_folder="books",
                                file_name=f"{cleaned_book_id}. {title}",
                            )
                        else:
                            logging.info(
                                f"В книге с id {cleaned_book_id} не найден текст"
                            )

                    if not skip_img:
                        cover_url = urljoin(response.url, image_path)
                        image = fetch_book_response(url=cover_url)
                        _, img_ext = tuple(image_path.split("."))
                        save_to_file(
                            content=image.content,
                            directory=dest_folder,
                            name_folder="image",
                            file_name=title,
                            extension=img_ext,
                        )

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
                    logging.info(
                        f"Не удалось загрузить книгу с id = {str(cleaned_book_id)}"
                    )
                    attempt += 1
                    sleep(1)
                    continue
                except requests.ConnectionError:
                    logging.info("Не удалось подключиться к серверу")
                    attempt += 1
                    sleep(1)
                    continue

    save_books_to_json_file(dest_folder, all_books)
