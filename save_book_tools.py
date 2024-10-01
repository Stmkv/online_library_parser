import os


def save_book_comments(comments, book_name):
    os.makedirs("Comments", exist_ok=True)
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
