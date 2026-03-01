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
        if path.is_file(): path.unlink(missing_ok=True)

class TestTypstAction(unittest.TestCase):

    # store path to python interpreter.
    python_path = 'python3'
    
    # In routines below, path is a list with each whitespace separated command line arg
    # in a separate list item.

    # Gitlab flow calls entrypoint.py with three args. If an ara is not provided in the
    # action yml file, a null string is passed into that arg. All three args must be passed.  

    def test_run_with_source_file_arg(self):
        # Compile a file using source file argument, passing in a file name.
        remove_glob('tests/*.pdf')          # clean up any existing output artifacts first
        command = [self.python_path, 'entrypoint.py', 'tests/math.typ', '', '']
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode,0)
        self.assertTrue(Path.exists(Path('tests/math.pdf')))
        self.assertFalse(Path.exists(Path('tests/valid.pdf')))

    def test_run_with_wildcard_arg(self):
        # Compile a file using source file argument, passing in a file name.
        remove_glob('tests/*.pdf')          # clean up any existing output artifacts first
        command = [self.python_path, 'entrypoint.py', 'tests/*.typ', '', '']
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode,0)
        self.assertTrue(Path.exists(Path('tests/math.pdf')))
        self.assertTrue(Path.exists(Path('tests/valid.pdf')))

    def test_run_with_multiline_source_file_arg(self):
        # Compile a file using source file argument, passing in a file name.
        remove_glob('tests/*.pdf')          # clean up any existing output artifacts first
        command = [self.python_path, 'entrypoint.py', 'tests/math.typ\ntests/valid.typ', '', '']
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode,0)
        self.assertTrue(Path.exists(Path('tests/math.pdf')))
        self.assertTrue(Path.exists(Path('tests/valid.pdf')))

    def test_run_with_directory_as_arg(self):
        # Compile a file using source file argument, passing in a directory name. 
        # Note that the directory contains an invalid test file, so returncode will be 1.
        remove_glob('tests/*.pdf')          # clean up any existing output artifacts first
        command = [self.python_path, 'entrypoint.py', 'tests', '', '']
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode,1)
        self.assertTrue(Path.exists(Path('tests/math.pdf')))
        self.assertTrue(Path.exists(Path('tests/valid.pdf')))

    def test_run_with_path_file_arg(self):
        # Compile a file using path file argument.  Should compile both test files.
        remove_glob('tests/*.pdf')          # clean up any existing output artifacts first
        command = [self.python_path, 'entrypoint.py', '', '', 'tests/files.txt']
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode,0)
        self.assertTrue(Path.exists(Path('tests/math.pdf')))
        self.assertTrue(Path.exists(Path('tests/valid.pdf')))

    def test_run_with_multiline_path_file_arg(self):
        # Compile a file using multiline path file argument.
        # Should result in a return code of 1 from entrypoint.py.
        remove_glob('tests/*.pdf')          # clean up any existing output artifacts first
        command = [self.python_path, 'entrypoint.py', '', '', 'tests/files.txt\ntests/files.txt']
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode,1)
        self.assertFalse(Path.exists(Path('tests/math.pdf')))
        self.assertFalse(Path.exists(Path('tests/valid.pdf')))

    def test_run_with_both_args(self):
        # Compile a file using source file argument and a path file argument.
        # Should result in a return code of 1 from entrypoint.py.
        remove_glob('tests/*.pdf')          # clean up any existing output artifacts first
        command = [self.python_path, 'entrypoint.py', 'tests/math.typ', '', 'tests/files.txt']
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode,1)
        self.assertFalse(Path.exists(Path('tests/math.pdf')))
        self.assertFalse(Path.exists(Path('tests/valid.pdf')))

    def test_run_with_invalid_file(self):
        # Compile an invalid source file.
        # Should result in a return code of 1 from entrypoint.py.
        command = [self.python_path, 'entrypoint.py', 'tests/bad/invalid.typ', '', '']
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode,1)

    def test_run_with_options(self):
        # Compile a file using source file argument and an options argument.
        # Should produce a file called deps.txt in the tests directory.
        remove_glob('tests/*.pdf')          # clean up any existing output artifacts first
        remove_file('tests/deps.txt')
        command = [self.python_path, 'entrypoint.py', 'tests/math.typ', '--deps=tests/deps.txt', '']
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode,0)
        self.assertTrue(Path.exists(Path('tests/math.pdf')))
        self.assertTrue(Path.exists(Path('tests/deps.txt')))    

if __name__ == '__main__':
    unittest.main()