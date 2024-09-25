import os
from pathlib import Path

import requests

if not os.path.exists("books"):
    os.makedirs("books")


for id in range(1, 11):
    params = {"id": id}
    url = "https://tululu.org/txt.php"
    response = requests.get(url, params=params)
    response.raise_for_status()

    filename = f"books/Book_{id}.txt"
    with open(filename, "wb") as file:
        file.write(response.content)
