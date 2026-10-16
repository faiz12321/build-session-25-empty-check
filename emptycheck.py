"""emptycheck.py - list empty files and empty folders in a folder.

Read-only: it only looks. It never changes, moves or deletes anything.

An empty file holds nothing (0 bytes). An empty folder holds no files
anywhere inside it, so a folder that only holds other empty folders is
listed too. Paths are printed relative to the folder you check, with
forward slashes.

Usage:
    python emptycheck.py FOLDER
"""
import os
import sys


def display_path(path, root):
    """Path of path relative to root, with forward slashes."""
    return os.path.relpath(path, root).replace(os.sep, "/")


def find_empty(root):
    """Return (empty_files, empty_folders) under root, both sorted.

    empty_files: display paths of files that hold 0 bytes.
    empty_folders: display paths of folders that hold no files anywhere
    inside them. Unreadable entries are skipped.
    """
    empty_files = []
    empty_folders = []
    for dirpath, dirnames, filenames in os.walk(root):
        for name in filenames:
            full = os.path.join(dirpath, name)
            try:
                if os.path.getsize(full) == 0:
                    empty_files.append(display_path(full, root))
            except OSError:
                continue
        if dirpath != root and not filenames:
            try:
                has_files_inside = any(
                    files for _, _, files in os.walk(dirpath)
                )
            except OSError:
                continue
            if not has_files_inside:
                empty_folders.append(display_path(dirpath, root))
    return sorted(empty_files), sorted(empty_folders)


def main(argv):
    if len(argv) != 2 or argv[1] in ("-h", "--help"):
        print("Usage: python emptycheck.py FOLDER", file=sys.stderr)
        return 2
    root = argv[1]
    if not os.path.isdir(root):
        print("No such folder: " + root, file=sys.stderr)
        return 2
    empty_files, empty_folders = find_empty(root)
    print("Empty check")
    print("Folder: " + root)
    print()
    print("Files with nothing inside: " + str(len(empty_files)))
    for path in empty_files:
        print("  " + path)
    print()
    print("Folders that hold no files: " + str(len(empty_folders)))
    for path in empty_folders:
        print("  " + path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
