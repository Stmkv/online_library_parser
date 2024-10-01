import argparse
import logging
import os

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

from parser_response_tools import fetch_book_image, fetch_book_response, get_book
from save_book_tools import save_book_comments, save_book_genre

logging.basicConfig(level=logging.DEBUG)


def save_book_image(cover, img_ext, book_name):
    os.makedirs("Images", exist_ok=True)
    with open(f"./{'Images'}/{book_name}.{img_ext}", "wb") as f:
        f.write(cover)


def save_book_txt(id, book, book_name):
    os.makedirs("Books", exist_ok=True)
    with open(f"./{"Books"}/{id}. {book_name}.txt", "wb") as f:
        f.write(book)


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
        try:
            book = get_book(book_id)
            response = fetch_book_response(book_id)
            title, author, image_path, comments, genres = parse_book_page(response)
            save_book_txt(book_id, book, title)
            image = fetch_book_image(image_path)
            _, img_ext = tuple(image_path.split("."))
            save_book_image(image, img_ext, title)
            save_book_comments(comments, title)
            save_book_genre(genres, title)
        except requests.HTTPError:
            logging.info("Не удалось загрузить книгу с id = " + str(book_id))
            continue
