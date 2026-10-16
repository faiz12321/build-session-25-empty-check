# Empty file and empty folder finder

`emptycheck.py` lists zero-byte files and folders where it found no files.
It reads only, but skipped or unreadable entries can make the report incomplete.
A result is not a recommendation to delete anything. Directory links and
permission-limited trees need care; this is a small teaching tool, not an audit.

## Practise

Save the three Python files in a new empty lesson folder. Use Python 3:

    python make_sample.py
    python emptycheck.py sample
    python emptycheck.py sample/drafts
    python -m unittest -v

`make_sample.py` creates `sample` beside the script. It refuses an existing
sample path before writing. It never deletes or replaces an old sample folder.
If it refuses, use a different new lesson folder, not someone else's files.
The sample's cat.jpg is text practice bytes, not a real picture.

The checker prints relative paths with forward slashes. A folder holding only
empty folders can be listed along with those folders. An empty file may still
be a required placeholder.

## Tests and recordings

21 fixture tests cover report counts, error cases, unchanged source-tree
metadata, setup file/folder collision refusal, preserved existing bytes,
an unrelated nested file and repeat-run refusal. Every test creates its
fixtures inside a temporary directory, not the sample beside the lesson.

The repair was recorded twice on GitHub-hosted Windows and twice on Ubuntu.
See the included repair25 recordings. Displayed lesson output uses the first
Windows recording. Versions, test rendering and elapsed times can differ.
No macOS or Windows desktop session was tested. Fixture passes do not prove
safety or completeness on every real filesystem.

## License

MIT (see LICENSE).
