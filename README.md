# hotcrp2pdf

Convert HotCRP talk submissions to a PDF document.

## Synopsis

```bash
hotcrp2pdf submissions.json talks.pdf
```

- `submissions.json`: Path to the HotCRP submissions JSON file (required)
- `output.pdf`: Path for the output PDF file (required)
- `--cache-dir PATH`: Directory to store intermediate files (default: `$XDG_CACHE_HOME/hotcrp2pdf` or `~/.cache/hotcrp2pdf`)
- `--no-authors`: Exclude author information from the PDF
- `--title TEXT`: Custom title for the document (default: "Talk Submissions")
- `--verbose, -v`: Enable verbose output
- `--help`: Show help message

## Description

`hotcrp2pdf` is a command-line tool that converts HotCRP (Hot Conference Review Platform) talk submissions from JSON format into a well-formatted PDF document. The tool processes submission data, formats it using markdown templates, and generates a professional PDF with a table of contents and organized sections for each submission.

## Features

- **JSON to PDF conversion**: Converts HotCRP submission JSON files to formatted PDF documents
- **One page of paper per submission:** Prints submissions into separate pages to aid reshuffling, grouping, etc.
- **Customizable output**: Options to include/exclude authors, customize document title
- **Error handling**: Graceful handling of malformed submissions with detailed error reporting

## Installation

### Using Nix

```bash
nix profile install github:your-username/hotcrp2pdf
```

### Using uv (requires pandoc, texlive)

First, ensure you have the required system dependencies `pandoc`, `texlive` then install via

```bash
uv tool install https://github.com/your-username/hotcrp2pdf
```

