import unittest
import subprocess
from pathlib import Path

def remove_file(filename:str):
    '''
    Removes a file without throwing an exception if the file does not exist.
    '''
    Path(filename).unlink(missing_ok=True)

def remove_glob(pattern: str):
    '''
    Deletes all files matching the given glob pattern. Any directories
    matching the pattern are ignored. This is useful in tests for cleaning
    up generated artifacts before running the command under test.
    '''
    base = Path() # set root path for the glob
    for path in base.glob(pattern):
        if path.is_file():
            path.unlink(missing_ok=True)

class TestAddFunction(unittest.TestCase):

    # TODO Figure out why I need whole path to python to avoid "file not found exception"
    python_path = '/opt/homebrew/bin/python3'

    # In routines below, path is a list with each whitespace separated command line arg
    # in a separate list item.

    # Gitlab flow calls entrypoint.py with three args. If an ara is not provided in the
    # action yml file, a null string is passed into that arg. All three args must be passed.  

    def test_run_with_source_file_arg(self):
        # Compile a file using source file argument
        remove_glob('tests/*.pdf')          # clean up any existing output artifacts first
        command = ['/opt/homebrew/bin/python3', 'entrypoint.py', 'tests/math.typ', '', '']
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode,0)
        self.assertTrue(Path.exists(Path('tests/math.pdf')))

    def test_run_with_path_file_arg(self):
        # Compile a file using source file argument
        remove_glob('tests/*.pdf')          # clean up any existing output artifacts first
        command = ['/opt/homebrew/bin/python3', 'entrypoint.py', '', '', 'tests/files.txt']
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode,0)
        self.assertTrue(Path.exists(Path('tests/math.pdf')))
        self.assertTrue(Path.exists(Path('tests/valid.pdf')))

    def test_run_with_both_args(self):
        # Compile a file using source file argument and a path file argument.
        # Should result in a return code of 1 from entrypoint.py.
        remove_glob('tests/*.pdf')          # clean up any existing output artifacts first
        command = ['/opt/homebrew/bin/python3', 'entrypoint.py', 'tests/math.typ', '', 'tests/files.txt']
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode,1)
        self.assertFalse(Path.exists(Path('tests/math.pdf')))
        self.assertFalse(Path.exists(Path('tests/valid.pdf')))

    def test_run_with_options(self):
        # Compile a file using source file argument and an options argument.
        # Should produce a file called deps.txt in the tests directory.
        remove_glob('tests/*.pdf')          # clean up any existing output artifacts first
        remove_file('tests/deps.txt')
        command = ['/opt/homebrew/bin/python3', 'entrypoint.py', 'tests/math.typ', '--deps=tests/deps.txt', '']
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode,0)
        self.assertTrue(Path.exists(Path('tests/math.pdf')))
        self.assertTrue(Path.exists(Path('tests/deps.txt')))    

if __name__ == '__main__':
    unittest.main()