"""make_sample.py - create a made-up practice folder for the lesson.

Creates a folder called "sample" next to this script, with real text
files, two empty files, and some empty folders, including one folder
that only holds another empty folder. Run it again any time; it first
removes the old sample folder.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLE = os.path.join(HERE, "sample")


def make_file(relative, text):
    path = os.path.join(SAMPLE, *relative.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as handle:
        handle.write(text)


def main():
    if os.path.isdir(SAMPLE):
        shutil.rmtree(SAMPLE)
    os.makedirs(SAMPLE)
    make_file("notes.txt", "Milk, eggs, bread\n")
    make_file("todo.txt", "")
    make_file("drafts/letter.txt", "Dear Sam,\n")
    make_file("drafts/ideas.txt", "")
    make_file("photos/cat.jpg", "not a real photo, just practice bytes\n")
    os.makedirs(os.path.join(SAMPLE, "backups", "old"))
    os.makedirs(os.path.join(SAMPLE, "exports"))
    print("Sample folder ready: " + SAMPLE)
    print("It holds 5 files (2 of them empty) and 3 folders that hold no files.")


if __name__ == "__main__":
    main()
