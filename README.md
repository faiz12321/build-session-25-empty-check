# Find empty fictional files and folders

Save three source files in a NEW empty lesson folder.

    python make_sample.py
    python emptycheck.py sample
    python -m unittest -v

Two Windows and two Ubuntu full replays run exact visible source versions. Final 35 small fixture tests pass (Unix pipe skips on Windows); symlink creation can skip where unavailable. Displayed stdout is first Windows output, not normalized or mixed. Pair differences are unittest time and the unique temporary path in the missing-folder metadata error.
Link/error changes only: refuse root/ancestor and tree symbolic links/reparse points, hardlinks, special entries and traversal. A metadata safety walk precedes ordinary counting so skipped aliases cannot make an unvisited folder look empty. Read/list/metadata errors now stop with incomplete exit 2 instead of silent skips or false clean success. Setup refuses linked parents/traversal and existing sample paths, without reset or deletion.
Ordinary zero-byte file detection, recursive empty-folder definition, relative display paths and sorting remain unchanged. Empty means zero bytes or no files below a folder, not safe or unneeded. Do not delete anything based on this report alone. Original repeated walks remain; large/deep trees can take time. Missing-folder errors now include their absolute temporary path.
The checker has no write/move/delete/network code and opens no file contents. No total size/time/resource limit, atomic snapshot or hostile-race defense. Stop editors/sync; entries can change between safety and count walks. Paths can be private. Small fictional fixtures are not proof on every filesystem. No desktop Windows/macOS recording. Recorder removes only its own temporary fixture folder. Decisions and feedback are teaching text, not recorded output.

MIT code. Python separately licensed/not included.

Reference: https://docs.python.org/3/library/os.html

Windows pair: https://github.com/faiz12321/lesson-lab/actions/runs/38974401838
Ubuntu pair: https://github.com/faiz12321/lesson-lab/actions/runs/38974644526
