"""Script to compile Typst source files."""
import logging
import subprocess
import sys
from pathlib import Path

def compile(filename: Path, options: list[str]) -> bool:
    """Compiles a Typst file with the specified global options.
    Returns True if the typst command exited with status 0, False otherwise.
    """
    command = ["typst"] + options + ["compile", str(filename)]
    logging.debug("Running: " + " ".join(command))

    result = subprocess.run(command, capture_output=True, text=True)
    try:
        result.check_returncode()
    except subprocess.CalledProcessError:
        logging.error(f"Compiling {filename} failed with stderr: \n {result.stderr}")
        return False

    return True

def read_path_file(file_path: Path) -> list[str]:
    """
    Reads all lines from a text file and appends them to a list of strings.
    Empty lines and lines containing only whitespace are skipped.
    """
    string_list = []
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                string_list.append(line)
    return string_list

def parse_source_files(source_files_input: list[str]) -> list[Path]:
    """
    Handles globs and directories in the source files argument.
    """
    source_files_paths = []
    for source_file in source_files_input:
        source_file = source_file.strip()
        if source_file == "":
            continue
        source_file_path = Path(source_file)
        if source_file_path.is_dir():
            source_files_paths.extend(source_file_path.glob("**/*.typ"))
        elif source_file_path.is_file():
            source_files_paths.append(source_file_path)
        elif "*" in source_file:
            source_files = list(Path.cwd().glob(source_file))
            if not source_files:
                logging.error(f"No matching files found for {source_file}.")
                logging.debug(f"Current directory: {Path.cwd()}")
                logging.debug(f"First 10 files: {list(Path.cwd().iterdir())[:10]}")
            else:
                source_files_paths.extend(source_files)
        else:
            logging.error(f"Source file {source_file} does not exist.")
    return source_files_paths

def main():
    logging.basicConfig(level=logging.INFO)

    # Parse the positional arguments, expected in the following form
    #   1. The Typst files to compile in a line separated string.
    #   2. The global Typst CLI options, in a line separated string. 
    # In each case, means each whitespace separated field should be on its own line.
    
    # Convert line separated source file path args to a list of strings, ignoring blank lines
    file_list = []
    for arg_file in sys.argv[1].splitlines():
        arg_file = arg_file.strip()
        if arg_file == "":
            continue
        file_list.append(arg_file)
    
    # If we are using a path file, re-write the file list with lines from the path file
    # We will assume we have a path file if only one argument is provided and it 
    # has ".txt" as a file extension. 
    if len(file_list) == 1:
        arg_path = Path(file_list[0])
        if arg_path.is_file() and arg_path.suffix == ".txt":
            logging.info(f"Using path file contents to find source files.")
            file_list = read_path_file(arg_path)
    else:
        logging.info(f"Using arguments to find source files.")

    # Here we parse the file list, either from the argument list or from the path file
    # The parsing routine expands wildcards in the file list. 
    source_files = parse_source_files(file_list)
    logging.info(f"Found {len(source_files)} source files to compile.")

    # Convert line separated args for compiler options to a list of strings.
    options = sys.argv[2].splitlines()

    # Determine and log the version of typst compiler we are using
    version = subprocess.run(["typst", "--version"], capture_output=True, text=True).stdout
    logging.info(f"Using typst compiler version {version}.")

    # Compile source files, recording process status for each
    success: dict[str, bool] = {}
    for file in source_files:
        logging.info(f"Compiling {file}…")
        success[str(file)] = compile(file, options)

    # Log status of each compiler run.
    for file, status in success.items():
        logging.info(f"{file}: {'✔' if status else '❌'}")

    # Exit with error code if any runs did not succeed
    if not all(success.values()):
        sys.exit(1)

if __name__ == "__main__":
    main()