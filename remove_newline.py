import os
import re

def remove_extra_blank_lines_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = re.sub(r'((?:[ \t]*\n){2,})', '\n', content)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Cleaned: {filepath}")

def process_directory(root_folder):
    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith('.java'):
                filepath = os.path.join(dirpath, filename)
                remove_extra_blank_lines_from_file(filepath)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python remove_extra_blank_lines.py /path/to/java/code")
    else:
        process_directory(sys.argv[1])
