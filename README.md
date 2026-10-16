# Empty file and empty folder finder

`emptycheck.py` lists the empty files and empty folders inside a folder
you pick. It is read-only: it only looks, and it never changes, moves or
deletes anything. Run it first on the made-up `sample` folder from
`make_sample.py` before pointing it anywhere else.

- An **empty file** holds nothing (0 bytes).
- An **empty folder** holds no files anywhere inside it. A folder that
  only holds other empty folders is listed too, along with those
  folders.
- Paths are printed relative to the folder you check, with forward
  slashes.
- Entries the tool cannot read are skipped; the report only covers what
  it could see.

## Use

    python make_sample.py
    python emptycheck.py sample
    python emptycheck.py "C:\Users\you\Documents"

## Tests

    python -m unittest -v

Works on Windows, Mac and Linux with Python 3.10 or newer. Nothing to
install: it uses only what comes with Python.

## License

MIT (see LICENSE).
