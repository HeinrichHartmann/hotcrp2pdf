# hotcrp2pdf

Convert HotCRP talk submissions to a PDF document.

## Synopsis

```bash
hotcrp2pdf submissions.json out.pdf
```

## Description

`hotcrp2pdf` is a command-line tool that converts HotCRP (Hot Conference Review Platform) talk submissions from JSON format into a well-formatted PDF document. The tool processes submission data, formats it using markdown templates, and generates a professional PDF with a table of contents and organized sections for each submission.

## Features

- **JSON to PDF conversion**: Converts HotCRP submission JSON files to formatted PDF documents
- **XDG Base Directory compliant**: Uses `$XDG_CACHE_HOME/hotcrp2pdf` or `~/.cache/hotcrp2pdf` for intermediate files
- **Caching**: Uses a cache directory for intermediate files to speed up repeated conversions
- **Customizable output**: Options to include/exclude authors, customize document title
- **Professional formatting**: Generates PDFs with table of contents, proper sectioning, and clean typography
- **Error handling**: Graceful handling of malformed submissions with detailed error reporting

## Installation

### Using Nix

```bash
nix profile install github:your-username/hotcrp2pdf
```

### Using uv (requires pandoc, texlive)

First, ensure you have the required system dependencies:

```bash
# On macOS with Homebrew
brew install pandoc texlive

# On Ubuntu/Debian
sudo apt-get install pandoc texlive-xetex texlive-latex-extra

# On Fedora
sudo dnf install pandoc texlive-xetex
```

Then install the tool:

```bash
uv tool install https://github.com/your-username/hotcrp2pdf
```

### Development Installation

```bash
git clone https://github.com/your-username/hotcrp2pdf
cd hotcrp2pdf
uv sync
```

## Usage

### Basic Usage

```bash
hotcrp2pdf submissions.json talks.pdf
```

### Advanced Options

```bash
# Exclude author information
hotcrp2pdf --no-authors submissions.json talks.pdf

# Use custom cache directory
hotcrp2pdf --cache-dir ./cache submissions.json talks.pdf

# Custom document title
hotcrp2pdf --title "SREcon 2025 Submissions" submissions.json talks.pdf

# Verbose output
hotcrp2pdf --verbose submissions.json talks.pdf
```

### Command Line Options

- `submissions.json`: Path to the HotCRP submissions JSON file (required)
- `output.pdf`: Path for the output PDF file (required)
- `--cache-dir PATH`: Directory to store intermediate files (default: `$XDG_CACHE_HOME/hotcrp2pdf` or `~/.cache/hotcrp2pdf`)
- `--no-authors`: Exclude author information from the PDF
- `--title TEXT`: Custom title for the document (default: "Talk Submissions")
- `--verbose, -v`: Enable verbose output
- `--help`: Show help message

## Input Format

The tool expects a JSON file containing an array of HotCRP submission objects. Each submission should contain fields such as:

- `pid`: Paper/submission ID
- `title`: Submission title
- `authors`: Array of author objects with `first`, `last`, `email`, `affiliation`
- `proposal_length`: Duration/length of the proposed talk
- `long_description_program_committee`: Main description
- `session_outline`: Outline of the session
- `audience_take_aways`: What audience will learn
- `tags`: Array of tag objects
- Additional metadata fields

## Output Format

The generated PDF includes:

1. **Title page** with document title and submission count
2. **Table of contents** with links to each submission
3. **Individual submissions** with:
   - Submission ID and title
   - Speaker information (if enabled)
   - Duration/length
   - Tags
   - Description
   - Session outline
   - Audience take-aways
   - Program committee notes

## Dependencies

- **Python 3.9+**
- **pandoc**: For converting markdown to PDF
- **LaTeX/XeTeX**: For PDF generation (included in texlive distributions)
- **Python packages**: click, jinja2, dataclasses-json

## Development

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/your-username/hotcrp2pdf
cd hotcrp2pdf

# Enter Nix shell (if using Nix)
nix develop

# Or use uv for development
uv sync
```

### Running Tests

```bash
uv run python -m pytest tests/
```

### Code Structure

- `hotcrp2pdf/models.py`: Data models for submissions, talks, authors
- `hotcrp2pdf/converter.py`: Core conversion logic
- `hotcrp2pdf/main.py`: CLI interface
- `flake.nix`: Nix development environment with pandoc and LaTeX

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Troubleshooting

### Common Issues

**"pandoc not found"**
- Install pandoc using your system package manager or the official installer

**"xelatex not found"**
- Install a complete LaTeX distribution (e.g., texlive-full or mactex)

**"Permission denied" errors**
- Check write permissions for the output directory
- Ensure the cache directory is writable

**Empty or malformed PDF output**
- Check that the input JSON file is valid
- Use `--verbose` flag to see detailed error messages
- Check the cache directory for intermediate markdown files

### Getting Help

- Open an issue on GitHub
- Check existing issues for similar problems
- Include verbose output and error messages when reporting bugs
