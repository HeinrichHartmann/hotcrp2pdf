# hotcrp2pdf

Convert HotCRP talk submissions to a PDF document.

## Synopsis

```bash
Usage: hotcrp2pdf [OPTIONS] COMMAND [ARGS]...

  Convert HotCRP talk submissions to PDF document.

Options:
  --tmp-dir PATH  Directory to store temporary files (default:
                  $XDG_RUNTIME_DIR/hotcrp2pdf or /tmp/hotcrp2pdf-{uid})
  -v, --verbose   Enable verbose output
  --help          Show this message and exit.

Commands:
  clear              Clear the temporary directory used by hotcrp2pdf.
  convert            Convert HotCRP talk submissions to PDF document.
  convert-abstracts  Convert abstracts.txt to PDF document.
```

## Description

`hotcrp2pdf` is a command-line tool that converts HotCRP (Hot Conference Review Platform) talk submissions from JSON format into a well-formatted PDF document. The tool processes submission data, formats it using markdown templates, and generates a professional PDF with a table of contents and organized sections for each submission.

## Features

- **JSON to PDF conversion**: Converts HotCRP submission JSON files to formatted PDF documents
- **One page of paper per submission:** Prints submissions into separate pages to aid reshuffling, grouping, etc.
- **Customizable output**: Options to include/exclude authors, customize document title
- **Error handling**: Graceful handling of malformed submissions with detailed error reporting

## Installation

Ensure you have the required system dependencies `pandoc`, `texlive`, and `poppler_utils`.
You can do so by running inside a nix shell:

```bash
nix develop github:HeinrichHartmann/hotcrp2pdf --command zsh
```

Next install the python tool via:

```bash
uv tool install 'git+https://github.com/HeinrichHartmann/hotcrp2pdf.git'
```

Now you should be able to use the tool like so:

```
hotcrp2pdf convert-abstracts ./abstracts.txt abstracts.pdf
```
