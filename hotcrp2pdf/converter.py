"""
PDF conversion functionality for hotcrp2pdf
"""

import json
import subprocess
import tempfile
import os
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Optional, Tuple
from .models import Talk


def get_tmp_dir() -> Path:
    """Get the default temporary directory following XDG Base Directory Specification."""
    xdg_runtime_dir = os.environ.get('XDG_RUNTIME_DIR')
    if xdg_runtime_dir:
        tmp_dir = Path(xdg_runtime_dir) / 'hotcrp2pdf'
    else:
        tmp_dir = Path('/tmp') / f'hotcrp2pdf-{os.getuid()}'
    
    tmp_dir.mkdir(parents=True, exist_ok=True)
    return tmp_dir


class HotCRPConverter:
    """Convert HotCRP submissions to PDF."""
    
    def __init__(self, tmp_dir: Optional[Path] = None):
        """Initialize the converter."""
        self.tmp_dir = tmp_dir or get_tmp_dir()
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        self.talks_dir = self.tmp_dir / "talks"
        self.talks_dir.mkdir(exist_ok=True)
        
        # Pandoc flags for consistent formatting
        self.pandoc_flags = [
            '--pdf-engine=xelatex',
            '-V', 'geometry:top=1.5cm,bottom=1.5cm,left=1.5cm,right=1.5cm',
            '-V', 'fontsize=10pt',
            '-V', 'papersize=a4',
            '-V', 'urlcolor=blue',
            '-V', 'linkcolor=blue',
            '-V', 'toccolor=blue',
            '-V', 'maxlistdepth=10'
        ]
    
    def _run_pandoc(self, input_file: Path, output_file: Path, extra_flags: List[str] = None) -> bool:
        """Run pandoc with standard flags and optional extra flags."""
        cmd = ['pandoc', str(input_file), '-o', str(output_file)] + self.pandoc_flags
        if extra_flags:
            cmd.extend(extra_flags)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error running pandoc: {e}")
            print(f"Command: {' '.join(cmd)}")
            print(f"Stdout: {e.stdout}")
            print(f"Stderr: {e.stderr}")
            return False
        except FileNotFoundError:
            print("Error: pandoc not found. Please install pandoc.")
            return False
    
    def _get_pdf_page_count(self, pdf_file: Path) -> int:
        """Get the number of pages in a PDF file."""
        try:
            result = subprocess.run(
                ['pdfinfo', str(pdf_file)],
                capture_output=True,
                text=True,
                check=True
            )
            for line in result.stdout.splitlines():
                if line.startswith('Pages:'):
                    return int(line.split(':')[1].strip())
            return 0
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"Error getting page count for {pdf_file}")
            return 0
        
    def _create_blank_page(self) -> Path:
        """Create a blank page if needed."""
        blank_page = self.tmp_dir / "blank.pdf"
        if blank_page.exists():
            return blank_page
    
        # Create a proper LaTeX document for the blank page
        blank_tex = self.tmp_dir / "blank.tex"
        with open(blank_tex, 'w') as f:
            f.write("""
\\documentclass[a4paper,10pt]{article}
\\usepackage[margin=1.5cm]{geometry}
\\begin{document}
\\thispagestyle{empty}
(blank)
\\end{document}
""")
        # Use pdflatex directly instead of pandoc for the blank page
        cmd = ['pdflatex', '-interaction=nonstopmode', str(blank_tex)]
        subprocess.run(cmd, cwd=str(self.tmp_dir), check=True, capture_output=True)
        os.replace(str(blank_tex).replace('.tex', '.pdf'), str(blank_page))
        return blank_page

    def _ensure_pdf_pages(self, pdf_file: Path, target_pages: int) -> bool:
        """Ensure PDF has exactly target_pages by adding blank pages or truncating."""
        current_pages = self._get_pdf_page_count(pdf_file)
        if current_pages == target_pages:
            return True
        blank_page = self._create_blank_page()
        # Handle page count adjustment
        try:
            if current_pages < target_pages:
                # Add blank pages
                temp_output = str(pdf_file) + '.tmp'
                cmd = ['pdfunite', str(pdf_file), str(blank_page), temp_output]
                subprocess.run(cmd, check=True, capture_output=True)
                os.replace(temp_output, str(pdf_file))
            elif current_pages > target_pages:
                # Truncate to target pages
                temp_output = str(pdf_file) + '.tmp'
                cmd = ['pdfjam', str(pdf_file), f'1-{target_pages}', '-o', temp_output]
                subprocess.run(cmd, check=True, capture_output=True)
                os.replace(temp_output, str(pdf_file))
            
            # Verify the final page count
            final_pages = self._get_pdf_page_count(pdf_file)
            if final_pages != target_pages:
                print(f"Warning: Failed to adjust page count. Expected {target_pages}, got {final_pages}")
                return False
                
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Error adjusting page count: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error adjusting page count: {e}")
            return False
    
    def generate_title_page(self, title: str, num_talks: int) -> Optional[Path]:
        """Generate title page PDF."""
        title_md = self.tmp_dir / "title.md"
        title_pdf = self.tmp_dir / "title.pdf"
        
        with open(title_md, 'w') as f:
            f.write(f"# {title}\n\nTotal submissions: {num_talks}\n")
        
        if self._run_pandoc(title_md, title_pdf):
            self._ensure_pdf_pages(title_pdf, 1)
            return title_pdf
        return None
    
    def generate_toc(self, talks: List[Talk]) -> Optional[Path]:
        """Generate table of contents PDF."""
        toc_md = self.tmp_dir / "toc.md"
        toc_pdf = self.tmp_dir / "toc.pdf"
        
        with open(toc_md, 'w') as f:
            f.write("# Table of Contents\n\n")
            for talk in sorted(talks, key=lambda t: t.pid):
                title_clean = talk.title.replace('#', '').strip()
                f.write(f"* [{talk.pid}. {title_clean}](#submission-{talk.pid})\n")
        
        if self._run_pandoc(toc_md, toc_pdf):
            # Ensure odd number of pages
            pages = self._get_pdf_page_count(toc_pdf)
            if pages % 2 == 0:
                self._ensure_pdf_pages(toc_pdf, pages + 1)
            return toc_pdf
        return None
    
    def generate_talk_pdf(self, talk: Talk, include_authors: bool) -> Optional[Path]:
        """Generate PDF for a single talk."""
        talk_md = self.talks_dir / f"talk_{talk.pid}.md"
        talk_pdf = self.talks_dir / f"talk_{talk.pid}.pdf"
        
        if talk_pdf.exists():
            print(f"Using cached PDF for talk {talk.pid}")
            return talk_pdf
        
        with open(talk_md, 'w') as f:
            f.write(talk.render_markdown(include_authors=include_authors))
        
        if self._run_pandoc(talk_md, talk_pdf):
            self._ensure_pdf_pages(talk_pdf, 2)  # Ensure exactly 2 pages
            return talk_pdf
        return None
    
    def load_submissions(self, json_file: Path) -> List[Talk]:
        """Load talk submissions from JSON file."""
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        talks = []
        for record in data:
            try:
                talk = Talk.from_record(record)
                talks.append(talk)
            except Exception as e:
                print(f"Warning: Failed to parse submission {record.get('pid', 'unknown')}: {e}")
        
        return talks
    
    def convert(self, json_file: Path, output_pdf: Path, 
                include_authors: bool = True, title: str = "Talk Submissions") -> bool:
        """Convert HotCRP submissions JSON to PDF with specific page requirements."""
        # Load submissions
        print(f"Loading submissions from {json_file}...")
        talks = self.load_submissions(json_file)
        print(f"Loaded {len(talks)} submissions")
        
        if not talks:
            print("No valid submissions found")
            return False
        
        # Generate title page
        print("Generating title page...")
        title_pdf = self.generate_title_page(title, len(talks))
        if not title_pdf:
            return False
        
        # Generate TOC
        print("Generating table of contents...")
        toc_pdf = self.generate_toc(talks)
        if not toc_pdf:
            return False
        
        # Generate individual talk PDFs in parallel
        print("Generating talk PDFs in parallel...")
        talk_pdfs = []
        failed_talks = []
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            # Submit all tasks
            future_to_talk = {
                executor.submit(self.generate_talk_pdf, talk, include_authors): talk
                for talk in talks
            }
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_talk):
                talk = future_to_talk[future]
                try:
                    talk_pdf = future.result()
                    if talk_pdf:
                        talk_pdfs.append((talk.pid, talk_pdf))  # Store PID with PDF path
                        print(f"✓ Generated PDF for talk {talk.pid}")
                    else:
                        failed_talks.append(talk.pid)
                        print(f"✗ Failed to generate PDF for talk {talk.pid}")
                except Exception as e:
                    failed_talks.append(talk.pid)
                    print(f"✗ Error processing talk {talk.pid}: {e}")
        
        if failed_talks:
            print(f"Warning: Failed to generate PDFs for {len(failed_talks)} talks: {failed_talks}")
        
        # Sort talk PDFs by PID before concatenating
        talk_pdfs.sort(key=lambda x: x[0])  # Sort by PID
        sorted_talk_pdfs = [pdf for _, pdf in talk_pdfs]  # Extract just the PDF paths
        
        # Concatenate all PDFs
        print("Concatenating PDFs...")
        pdf_files = [str(title_pdf), str(toc_pdf)] + [str(p) for p in sorted_talk_pdfs]
        cmd = ['pdfunite'] + pdf_files + [str(output_pdf)]            
        try:
            subprocess.run(cmd, check=True)
            print(f"Successfully created {output_pdf}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error concatenating PDFs: {e}")
            return False
