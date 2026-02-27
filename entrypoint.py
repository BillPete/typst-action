"""Script to compile Typst source files."""
import logging
import subprocess
import sys
from pathlib import Path

def compile(filename: Path, options: list[str]) -> bool:
    """
    Compiles a Typst file with the specified global options.
    Returns True if the typst command exited with status 0, False otherwise.
    """
    command = ["typst"] + options + ["compile", str(filename)]
    logging.debug("Running: " + " ".join(command))

    result = subprocess.run(command, capture_output=True, text=True)
    # TODO - use returncode option to make this try block unnecessary
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
    lines = []
    with open(file_path, "r") as f:
        for line in f:
            lines.append(line)
        return strip_all_lines(lines)

def parse_source_files(source_files_input: list[str]) -> list[Path]:
    """
    Creates a list of files to be compiled.
    Expands directories and globs while parsing.
    """
    source_files_paths = []
    for source_file in source_files_input:
        source_file_path = Path(source_file)
        if source_file_path.is_dir():
            # If a directory is given, grab names of all typst files in that directory
            source_files_paths.extend(source_file_path.glob("**/*.typ"))
        elif source_file_path.is_file():
            # If a file is given grab that file name
            source_files_paths.append(source_file_path)
        elif "*" in source_file or "?" in source_file or "[" in source_file:
            # Strings with * or ? or [] are potential globs
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

def strip_all_lines(input_list: list[str]) -> list[str]:
    """
    Strips all whitespace surrounding each line in a list of strings. 
    """
    output_list = []
    for line in input_list:
        line = line.strip()
        if line:
            output_list.append(line)
    return output_list

def main():
    logging.basicConfig(level=logging.INFO)

    # Parse the positional arguments, expected in the following form
    #   1. The Typst files to compile in a line separated string.
    #   2. The global Typst CLI options, in a line separated string. 
    #   3. The name of a txt file that contains a path on each line.
    # In each case, means each whitespace separated field should be on its own line.
    
    # Convert line separated args to a list of strings, ignoring blank lines
    file_list = strip_all_lines(sys.argv[1].splitlines())
    options   = strip_all_lines(sys.argv[2].splitlines())
    path_list = strip_all_lines(sys.argv[3].splitlines())

    if len(path_list) > 1:
        logging.error(f"Only one path file name may be processed.")
        sys.exit(1)
    if path_list and file_list:
        logging.error(f"Both path file and source file arguments were provided.")
        sys.exit(1) 

    # If we are using a path file, re-write the file list with lines from the path file
    if path_list:
        logging.info(f"Using path file contents to find source files.")
        file_list = read_path_file(path_list[0])
    else:
        logging.info(f"Using source file arguments to find source files.")

    # Here we parse the file list, either from the argument list or from the path file
    # The parsing routine expands directories or wildcards in the file list. 
    source_files = parse_source_files(file_list)
    logging.info(f"Found {len(source_files)} source files to compile.")

    # Determine and log the version of typst compiler we are using
    version = subprocess.run(["typst", "--version"], capture_output=True, text=True).stdout
    logging.info(f"Using typst compiler version {version}.")

    # Compile source files, recording compile process return status for each
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