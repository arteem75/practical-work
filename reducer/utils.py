def read_file(file_path: str) -> str:
    with open(file_path, 'r') as file:
        return file.read()


def update_file(file_path: str, content: str):
    with open(file_path, 'w') as file:
        file.write(content)
