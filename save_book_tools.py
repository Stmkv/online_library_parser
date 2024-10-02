import os


def save_to_file(content, directory, file_name, extension=None):
    os.makedirs(directory, exist_ok=True)
    if extension is not None:
        file_path = os.path.join(directory, f"{file_name}.{extension}")
        with open(file_path, "wb") as f:
            f.write(content)
    else:
        file_path = os.path.join(directory, f"{file_name}.txt")
        with open(file_path, "w") as file:
            for item in content:
                file.write(f"{item}\n\n")
