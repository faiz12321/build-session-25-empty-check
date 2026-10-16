"""make_sample.py - create a made-up practice folder for the lesson.

Creates a folder called "sample" next to this script, with real text
files, two empty files, and some empty folders, including one folder
that only holds another empty folder. It refuses any existing sample path before writing.
Nothing is deleted or replaced.
"""
import os
import stat
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLE = os.path.join(HERE, "sample")


def make_file(relative, text):
    path = os.path.join(SAMPLE, *relative.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "x", encoding="utf-8", newline="") as handle:
        handle.write(text)


def main():
    root = Path(SAMPLE).absolute()
    if '..' in root.parts:
        raise OSError('Parent-traversal paths are unsupported.')
    for parent in reversed(root.parents):
        info = parent.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise OSError('Linked/reparse-point parents are unsupported.')
    try:
        os.mkdir(SAMPLE)
    except FileExistsError:
        raise SystemExit("Stopped: sample already exists. Nothing was replaced or deleted.")
    make_file("notes.txt", "Milk, eggs, bread\n")
    make_file("todo.txt", "")
    make_file("drafts/letter.txt", "Dear Sam,\n")
    make_file("drafts/ideas.txt", "")
    make_file("photos/cat.jpg", "not a real photo, just practice bytes\n")
    os.makedirs(os.path.join(SAMPLE, "backups", "old"))
    os.makedirs(os.path.join(SAMPLE, "exports"))
    print("Created a new sample folder beside make_sample.py.")
    print("It holds 5 files (2 of them empty) and 3 folders that hold no files.")


if __name__ == "__main__":
    main()
