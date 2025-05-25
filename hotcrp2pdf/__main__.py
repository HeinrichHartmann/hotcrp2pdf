"""
Main CLI interface for hotcrp2pdf
"""

import click
import shutil
from pathlib import Path
from .converter import HotCRPConverter, get_tmp_dir


@click.group()
@click.option('--tmp-dir', type=click.Path(path_type=Path),
              help='Directory to store temporary files (default: $XDG_RUNTIME_DIR/hotcrp2pdf or /tmp/hotcrp2pdf-{uid})')
@click.option('--verbose', '-v', is_flag=True,
              help='Enable verbose output')
@click.pass_context
def cli(ctx, tmp_dir: Path, verbose: bool):
    """Convert HotCRP talk submissions to PDF document."""
    ctx.ensure_object(dict)
    ctx.obj['tmp_dir'] = tmp_dir
    ctx.obj['verbose'] = verbose


@cli.command()
@click.argument('submissions_json', type=click.Path(exists=True, path_type=Path))
@click.argument('output_pdf', type=click.Path(path_type=Path))
@click.option('--no-authors', is_flag=True,
              help='Exclude author information from the PDF')
@click.option('--title', default='Talk Submissions',
              help='Title for the document (default: "Talk Submissions")')
@click.pass_context
def convert(ctx, submissions_json: Path, output_pdf: Path, 
        no_authors: bool, title: str):
    """Convert HotCRP talk submissions to PDF document.
    
    SUBMISSIONS_JSON: Path to the HotCRP submissions JSON file
    OUTPUT_PDF: Path for the output PDF file
    """
    tmp_dir = ctx.obj['tmp_dir']
    verbose = ctx.obj['verbose']
    
    if verbose:
        click.echo(f"Converting {submissions_json} to {output_pdf}")
        if tmp_dir:
            click.echo(f"Using temporary directory: {tmp_dir}")
    
    # Create converter
    converter = HotCRPConverter(tmp_dir=tmp_dir)
    
    # Perform conversion
    include_authors = not no_authors
    success = converter.convert(
        json_file=submissions_json,
        output_pdf=output_pdf,
        include_authors=include_authors,
        title=title
    )
    
    if success:
        click.echo(f"✓ Successfully created {output_pdf}")
    else:
        click.echo("✗ Conversion failed", err=True)
        raise click.Abort()


@cli.command()
@click.pass_context
def clear(ctx):
    """Clear the temporary directory used by hotcrp2pdf."""
    tmp_dir = ctx.obj['tmp_dir'] or get_tmp_dir()
    verbose = ctx.obj['verbose']
    
    if verbose:
        click.echo(f"Clearing temporary directory: {tmp_dir}")
    
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
        click.echo(f"✓ Successfully cleared {tmp_dir}")
    else:
        click.echo(f"Temporary directory {tmp_dir} does not exist")


if __name__ == "__main__":
    cli(obj={}) 