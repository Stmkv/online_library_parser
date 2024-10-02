import os


def save_to_file(content, directory, file_name, extension="txt"):
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, f"{file_name}.{extension}")
    if type(content) is list:
        with open(file_path, "w") as file:
            for item in content:
                file.write(f"{item}\n\n")
    else:
        with open(file_path, "wb") as f:
            f.write(content)
