import contextlib
import io
from pathlib import Path
from unittest import mock
"""Tests for emptycheck.py."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "emptycheck.py")
sys.path.insert(0, HERE)
import emptycheck


def run_tool(*args):
    return subprocess.run(
        [sys.executable, TOOL] + list(args),
        capture_output=True, text=True, timeout=60,
    )


def make(root, relative, text=None):
    path = os.path.join(root, *relative.split("/"))
    if text is None:
        os.makedirs(path, exist_ok=True)
    else:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as handle:
            handle.write(text)


def snapshot_tree(root):
    snap = []
    for dirpath, dirnames, filenames in os.walk(root):
        for name in dirnames + filenames:
            full = os.path.join(dirpath, name)
            st = os.stat(full)
            snap.append((full, st.st_size, st.st_mtime_ns))
    return sorted(snap)


class FindEmptyTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.root, True)

    def test_empty_file_is_listed(self):
        make(self.root, "todo.txt", "")
        files, folders = emptycheck.find_empty(self.root)
        self.assertEqual(files, ["todo.txt"])

    def test_file_with_text_is_not_listed(self):
        make(self.root, "notes.txt", "hello")
        files, folders = emptycheck.find_empty(self.root)
        self.assertEqual(files, [])

    def test_empty_folder_is_listed(self):
        make(self.root, "drafts")
        files, folders = emptycheck.find_empty(self.root)
        self.assertEqual(folders, ["drafts"])

    def test_folder_with_a_file_is_not_listed(self):
        make(self.root, "drafts/letter.txt", "hi")
        files, folders = emptycheck.find_empty(self.root)
        self.assertEqual(folders, [])

    def test_folder_of_empty_folders_is_listed_with_child(self):
        make(self.root, "backups/old")
        files, folders = emptycheck.find_empty(self.root)
        self.assertEqual(folders, ["backups", "backups/old"])

    def test_nested_empty_file_uses_forward_slashes(self):
        make(self.root, "a/b/zero.txt", "")
        files, folders = emptycheck.find_empty(self.root)
        self.assertEqual(files, ["a/b/zero.txt"])
        self.assertNotIn(os.sep + os.sep, files[0])

    def test_results_are_sorted(self):
        make(self.root, "z.txt", "")
        make(self.root, "a.txt", "")
        files, folders = emptycheck.find_empty(self.root)
        self.assertEqual(files, ["a.txt", "z.txt"])

    def test_root_with_files_is_not_listed_as_empty(self):
        make(self.root, "notes.txt", "hi")
        files, folders = emptycheck.find_empty(self.root)
        self.assertEqual(folders, [])

    def test_deep_file_keeps_parents_off_the_list(self):
        make(self.root, "backups/old/keep.txt", "x")
        files, folders = emptycheck.find_empty(self.root)
        self.assertEqual(folders, [])


class CliTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.root, True)

    def test_report_lists_empty_file_and_folder(self):
        make(self.root, "todo.txt", "")
        make(self.root, "exports")
        make(self.root, "notes.txt", "hi")
        result = run_tool(self.root)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Files with nothing inside: 1", result.stdout)
        self.assertIn("  todo.txt", result.stdout)
        self.assertIn("Folders that hold no files: 1", result.stdout)
        self.assertIn("  exports", result.stdout)
        self.assertNotIn("notes.txt", result.stdout)

    def test_missing_folder_is_a_clear_error(self):
        result = run_tool(os.path.join(self.root, "nope"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("No such folder", result.stderr)

    def test_file_instead_of_folder_is_a_clear_error(self):
        make(self.root, "notes.txt", "hi")
        result = run_tool(os.path.join(self.root, "notes.txt"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("No such folder", result.stderr)

    def test_no_arguments_prints_usage(self):
        result = run_tool()
        self.assertEqual(result.returncode, 2)
        self.assertIn("python emptycheck.py FOLDER", result.stderr)

    def test_help_prints_usage(self):
        result = run_tool("--help")
        self.assertEqual(result.returncode, 2)
        self.assertIn("python emptycheck.py FOLDER", result.stderr)

    def test_tool_does_not_change_the_tree(self):
        make(self.root, "todo.txt", "")
        make(self.root, "exports")
        before = snapshot_tree(self.root)
        result = run_tool(self.root)
        self.assertEqual(result.returncode, 0, result.stderr)
        after = snapshot_tree(self.root)
        self.assertEqual(before, after)

    def test_report_shows_folder_as_given(self):
        with tempfile.TemporaryDirectory() as work:
            os.chdir(work)
            try:
                make("sample", "todo.txt", "")
                result = run_tool("sample")
            finally:
                os.chdir(HERE)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Folder: sample", result.stdout)


class SampleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = self.temp.name
        shutil.copyfile(os.path.join(HERE, "make_sample.py"),
                        os.path.join(self.work, "make_sample.py"))

    def setup_run(self):
        return subprocess.run([sys.executable, os.path.join(self.work, "make_sample.py")],
                              capture_output=True, text=True)

    def test_sample_folder_matches_the_lesson_counts(self):
        self.assertEqual(self.setup_run().returncode, 0)
        files, folders = emptycheck.find_empty(os.path.join(self.work, "sample"))
        self.assertEqual(files, ["drafts/ideas.txt", "todo.txt"])
        self.assertEqual(folders, ["backups", "backups/old", "exports"])

    def test_setup_refuses_existing_folder_without_change(self):
        sample = os.path.join(self.work, "sample")
        make(sample, "notes.txt", "USER DATA")
        make(sample, "unrelated/deep.txt", "KEEP")
        before = snapshot_tree(sample)
        result = self.setup_run()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Nothing was replaced or deleted", result.stderr)
        self.assertEqual(before, snapshot_tree(sample))
        with open(os.path.join(sample, "notes.txt")) as handle:
            self.assertEqual(handle.read(), "USER DATA")

    def test_setup_refuses_existing_file(self):
        sample = os.path.join(self.work, "sample")
        with open(sample, "w") as handle:
            handle.write("KEEP")
        self.assertNotEqual(self.setup_run().returncode, 0)
        with open(sample) as handle:
            self.assertEqual(handle.read(), "KEEP")

    def test_rerun_preserves_generated_folder_and_user_file(self):
        self.assertEqual(self.setup_run().returncode, 0)
        sample = os.path.join(self.work, "sample")
        make(sample, "new-user-file.txt", "KEEP")
        before = snapshot_tree(sample)
        self.assertNotEqual(self.setup_run().returncode, 0)
        self.assertEqual(before, snapshot_tree(sample))


class SafetyTests(unittest.TestCase):
    def test_source_has_no_write_calls(self):
        with open(TOOL) as handle:
            source = handle.read()
        for banned in ("shutil", "os.remove", "os.rmdir", "os.rename",
                       "os.makedirs", "open("):
            self.assertNotIn(banned, source)


class PathSafety(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name);self.root=self.base/'tree';self.root.mkdir()
        self.file=self.root/'zero';self.file.write_bytes(b'')
    def link(self,path,target,directory=False):
        try:path.symlink_to(target,target_is_directory=directory)
        except OSError:self.skipTest('Symlinks unavailable')
    def code(self,path):
        with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
            return emptycheck.main(['p',str(path)])
    def test_root_alias_refuses(self):
        p=self.base/'alias';self.link(p,self.root,True);self.assertEqual(self.code(p),2)
    def test_ancestor_alias_refuses(self):
        p=self.base/'alias';self.link(p,self.base,True);self.assertEqual(self.code(p/'tree'),2)
    def test_tree_file_alias_refuses(self):
        self.link(self.root/'alias',self.file);self.assertEqual(self.code(self.root),2)
    def test_tree_directory_alias_refuses(self):
        self.link(self.root/'alias',self.root,True);self.assertEqual(self.code(self.root),2)
    def test_tree_dangling_refuses(self):
        self.link(self.root/'alias',self.root/'missing');self.assertEqual(self.code(self.root),2)
    def test_tree_self_loop_refuses(self):
        p=self.root/'alias';self.link(p,p);self.assertEqual(self.code(self.root),2)
    def test_hardlink_refuses(self):
        os.link(self.file,self.root/'hard');self.assertEqual(self.code(self.root),2)
    def test_pipe_refuses(self):
        if not hasattr(os,'mkfifo'):self.skipTest('Unix pipe unavailable')
        os.mkfifo(self.root/'pipe');self.assertEqual(self.code(self.root),2)
    def test_traversal_refuses(self):self.assertEqual(self.code(self.root/'..'/'tree'),2)
    def test_metadata_error_refuses(self):
        with mock.patch.object(Path,'lstat',side_effect=OSError('forced')):self.assertEqual(self.code(self.root),2)
    def test_reparse_attribute_refuses(self):
        real=Path.lstat
        def fake(p,*a,**kw):
            value=real(p,*a,**kw)
            if p==self.file:return type('Reparse',(),{'st_mode':value.st_mode,'st_file_attributes':0x400})()
            return value
        with mock.patch.object(Path,'lstat',fake):self.assertEqual(self.code(self.root),2)
    def test_walk_error_refuses(self):
        def walk(root,onerror=None,**kw):
            onerror(PermissionError('forced'));return iter([])
        with mock.patch.object(emptycheck.os,'walk',walk):self.assertEqual(self.code(self.root),2)
    def test_setup_alias_parent_refuses(self):
        import make_sample
        p=self.base/'alias';self.link(p,self.root,True)
        with mock.patch.object(make_sample,'SAMPLE',str(p/'new')):
            with self.assertRaises(OSError):make_sample.main()
        self.assertFalse((self.root/'new').exists())
    def test_setup_traversal_refuses(self):
        import make_sample
        with mock.patch.object(make_sample,'SAMPLE',str(self.root/'..'/'new')):
            with self.assertRaises(OSError):make_sample.main()


if __name__ == "__main__":
    unittest.main()
