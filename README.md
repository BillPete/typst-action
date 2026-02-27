# Typst GitHub action

Build Typst documents using GitHub workflows.

This action uses the typst compiler to build pdf files 
## Arguments:

- ```source_file```
  - Accepts paths to one or more source files (or directories, or globs).
  - Multiple items must be provided as a multi-line string.
  - If the path leads to an existing file, that file will be compiled.
  - If a path leads to an existing directory, all ```.typ``` files in the directory will be compiled.
  - If the path contains wildcards, all files matching the pattern will be compiled. 
  - This argument is optional and is mutually exclusive with the ```path_file``` argument.  
- ```path_file```
  - Accepts a pathe to a text file that contains a list of paths (one path on each line).
  - Each line of the text file may contain a fie name, directory name, or wildcard pattern.
  - File names, directory names, and wildcard patterns will be treated as described above.
  - This argument is optional and is mutually exclusive with the ```source_file``` argument.
- ```options```
  - Accepts command line options that will be used for the typst compiler.
  - Each whitespace separated option must appear in a separate line of this argument.  
  - This argument is optional.
  
## Minimal example

The following `.github/workflows/build.yaml` action compiles `main.typ` on every push.

```yaml
name: Build Typst document
on: push

jobs:
  build_typst_documents:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      - name: Typst
        uses: BillPete/typst-action@main
        with:
          source_file: main.typ
```

## Longer example

Here we compile multiple files on each push, and publish all the PDFs in a tagged and timestamped release when the commit is tagged.

```yaml
name: Build Typst document
on: [push, workflow_dispatch]

permissions:
  contents: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Typst
        uses: lvignoli/typst-action@main
        with:
          source_file: |
            first_file.typ
            second_file.typ
            third_and_final_file.typ

      - name: Upload PDF file
        uses: actions/upload-artifact@v3
        with:
          name: PDF
          path: *.pdf

      - name: Get current date
        id: date
        run: echo "DATE=$(date +%Y-%m-%d-%H:%M)" >> $GITHUB_ENV

      - name: Release
        uses: softprops/action-gh-release@v1
        if: github.ref_type == 'tag'
        with:
          name: "${{ github.ref_name }} — ${{ env.DATE }}"
          files: main.pdf
```
## Notes

- This action runs on the docker image shipped with the latest Typst.
  As long as Typst is in v0, changes of the CLI API are to be expected, breaking the workflow.

