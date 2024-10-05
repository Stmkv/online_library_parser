from urllib.parse import urljoin

from bs4 import BeautifulSoup

from parser_response_tools import fetch_book_response

BASE_URL = "https://tululu.org/"

url = "https://tululu.org/l55/"
response = fetch_book_response(url)

soup = BeautifulSoup(response.text, "lxml")
carts_books = soup.find_all("div", class_="bookimage")

for id_book in carts_books:
    part_link = id_book.find("a")["href"]
    link = urljoin(BASE_URL, part_link)
