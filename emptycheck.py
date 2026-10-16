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
import stat
from pathlib import Path


def safe_input(value, directory=False):
    path = Path(value).absolute()
    if '..' in path.parts:
        raise OSError('Parent-traversal paths are unsupported.')
    for part in [*reversed(path.parents), path]:
        info = part.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise OSError('Links/reparse points are unsupported.')
    info = path.lstat()
    if directory:
        if not stat.S_ISDIR(info.st_mode):
            raise NotADirectoryError('Expected an ordinary directory.')
    elif not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise OSError('Expected an ordinary singly linked file.')
    return path







def display_path(path, root):
    """Path of path relative to root, with forward slashes."""
    return os.path.relpath(path, root).replace(os.sep, "/")


def find_empty(root):
    """Return (empty_files, empty_folders) under root, both sorted.

    empty_files: display paths of files that hold 0 bytes.
    empty_folders: display paths of folders that hold no files anywhere
    inside them. Unsafe aliases and unreadable entries refuse with an error.
    """
    safe_input(root, directory=True)
    def fail(error):
        raise error
    # Refuse aliases/errors before totals, rather than label unvisited data empty.
    for here, dirs, names in os.walk(root, onerror=fail):
        for name in dirs:
            safe_input(os.path.join(here, name), directory=True)
        for name in names:
            safe_input(os.path.join(here, name))
    empty_files = []
    empty_folders = []
    for dirpath, dirnames, filenames in os.walk(root, onerror=fail):
        for name in filenames:
            full = os.path.join(dirpath, name)
            try:
                if os.path.getsize(full) == 0:
                    empty_files.append(display_path(full, root))
            except OSError:
                raise
        if dirpath != root and not filenames:
            try:
                has_files_inside = any(
                    files for _, _, files in os.walk(dirpath, onerror=fail)
                )
            except OSError:
                raise
            if not has_files_inside:
                empty_folders.append(display_path(dirpath, root))
    return sorted(empty_files), sorted(empty_folders)


def main(argv):
    if len(argv) != 2 or argv[1] in ("-h", "--help"):
        print("Usage: python emptycheck.py FOLDER", file=sys.stderr)
        return 2
    root = argv[1]
    try:
        safe_input(root, directory=True)
    except OSError as error:
        print("No such folder: " + root + " (" + str(error) + ")", file=sys.stderr)
        return 2
    if not os.path.isdir(root):
        print("No such folder: " + root, file=sys.stderr)
        return 2
    try:
        empty_files, empty_folders = find_empty(root)
    except OSError as error:
        print("Could not complete empty check: " + str(error), file=sys.stderr)
        return 2
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
