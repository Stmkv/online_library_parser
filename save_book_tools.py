import os


def save_to_file(content, directory, name_folder, file_name, extension="txt"):
    folder = os.path.join(directory, name_folder)
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"{file_name}.{extension}")
    if type(content) is list:
        with open(file_path, "w", encoding="utf-8") as file:
            for item in content:
                file.write(f"{item}\n\n")
    else:
        with open(file_path, "wb") as f:
            f.write(content)
