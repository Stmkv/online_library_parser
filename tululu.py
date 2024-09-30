import argparse
import os

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError()


def save_book_image(cover, img_ext, book_name):
    if not os.path.exists("Images"):
        os.makedirs("Images")
    with open(f"./{'Images'}/{book_name}.{img_ext}", "wb") as f:
        f.write(cover)
        f.close()


def save_book_txt(id, book, book_name):
    if not os.path.exists("Books"):
        os.makedirs("Books")
    with open(f"./{"Books"}/{id}. {book_name}.txt", "wb") as f:
        f.write(book)
        f.close()


def save_book_comments(comments, book_name):
    if not os.path.exists("Comments"):
        os.makedirs("Comments")
    with open(f"./{"Comments"}/{book_name}.txt", "w") as file:
        for comment in comments:
            file.write(f"{comment}\n\n")
        file.close()


def save_book_genre(genres, book_name):
    if not os.path.exists("Genres"):
        os.makedirs("Genres")
    with open(f"./{"Genres"}/{book_name}.txt", "w") as file:
        for genre in genres:
            file.write(f"{genre}\n\n")
        file.close()


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


def fetch_book_info(book_id):
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


def get_range():
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
    left_border, right_border = get_range()
    for id in range(left_border, right_border + 1):
        try:
            book = get_book(id)
            response_info = fetch_book_info(id)
            title, author, image_path, comments, genres = parse_book_page(response_info)
            save_book_txt(id, book, title)
            image = fetch_book_image(image_path)
            _, img_ext = tuple(image_path.split("."))
            save_book_image(image, img_ext, title)
            save_book_comments(comments, title)
            save_book_genre(genres, title)
        except requests.HTTPError:
            continue
