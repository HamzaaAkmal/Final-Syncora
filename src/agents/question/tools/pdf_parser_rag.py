#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PDF Parser using PyPDF2 for RAG-based exam processing

Replaces MinerU dependency with simple PyPDF2 text extraction.
"""

from datetime import datetime
import json
from pathlib import Path
import shutil
from typing import Optional

import PyPDF2


def extract_pdf_text(pdf_path: str) -> tuple[str, dict]:
    """
    Extract text from PDF using PyPDF2.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Tuple of (full_text, metadata dict with page info)
    """
    pdf_path = Path(pdf_path).resolve()
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    if not pdf_path.suffix.lower() == ".pdf":
        raise ValueError(f"File is not PDF format: {pdf_path}")
    
    text_pages = []
    full_text = ""
    
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)
            
            for page_num in range(num_pages):
                page = reader.pages[page_num]
                page_text = page.extract_text() or ""
                text_pages.append({
                    "page": page_num + 1,
                    "text": page_text
                })
                full_text += f"\n--- Page {page_num + 1} ---\n{page_text}"
        
        metadata = {
            "filename": pdf_path.name,
            "num_pages": num_pages,
            "pages": text_pages,
            "extracted_at": datetime.now().isoformat()
        }
        
        return full_text.strip(), metadata
        
    except Exception as e:
        raise RuntimeError(f"Error extracting PDF text: {str(e)}")


def parse_pdf_simple(
    pdf_path: str,
    output_base_dir: str = None
) -> tuple[bool, Optional[Path]]:
    """
    Parse PDF and save extracted text to output directory.
    
    This replaces MinerU parsing with simple PyPDF2 extraction.
    
    Args:
        pdf_path: Path to PDF file
        output_base_dir: Base path for output directory
        
    Returns:
        Tuple of (success: bool, output_dir: Path or None)
    """
    try:
        pdf_path = Path(pdf_path).resolve()
        
        print(f"✓ Using PyPDF2 for PDF extraction")
        print(f"📄 PDF file: {pdf_path}")
        
        # Extract text
        full_text, metadata = extract_pdf_text(str(pdf_path))
        
        if not full_text.strip():
            print("⚠️ Warning: No text extracted from PDF")
            return False, None
        
        # Setup output directory
        script_dir = Path(__file__).parent.parent.parent.parent.parent
        if output_base_dir is None:
            output_base_dir = script_dir / "data" / "user" / "question" / "mimic_papers"
        else:
            output_base_dir = Path(output_base_dir)
        
        output_base_dir.mkdir(parents=True, exist_ok=True)
        
        # Create output directory for this PDF
        pdf_name = pdf_path.stem
        output_dir = output_base_dir / pdf_name
        
        if output_dir.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = output_base_dir / f"{pdf_name}_backup_{timestamp}"
            print(f"⚠️ Directory already exists, backing up to: {backup_dir.name}")
            shutil.move(str(output_dir), str(backup_dir))
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create 'auto' subdirectory for compatibility with existing workflow
        auto_dir = output_dir / "auto"
        auto_dir.mkdir(parents=True, exist_ok=True)
        
        # Save extracted text as markdown
        md_file = auto_dir / f"{pdf_name}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"# {pdf_name}\n\n")
            f.write(full_text)
        
        print(f"📝 Saved markdown: {md_file.name}")
        
        # Save metadata as JSON
        meta_file = auto_dir / f"{pdf_name}_metadata.json"
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"📋 Saved metadata: {meta_file.name}")
        
        # Create content_list.json for compatibility
        content_list = []
        for page_info in metadata.get("pages", []):
            content_list.append({
                "type": "text",
                "page": page_info["page"],
                "text": page_info["text"]
            })
        
        content_file = auto_dir / f"{pdf_name}_content_list.json"
        with open(content_file, 'w', encoding='utf-8') as f:
            json.dump(content_list, f, ensure_ascii=False, indent=2)
        
        print(f"📋 Saved content list: {content_file.name}")
        
        # Create empty images directory for compatibility
        images_dir = auto_dir / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 Output directory: {output_dir}")
        print(f"✓ PDF parsing completed!")
        
        return True, output_dir
        
    except Exception as e:
        print(f"✗ Error parsing PDF: {str(e)}")
        return False, None


def get_pdf_text_for_llm(pdf_path: str) -> str:
    """
    Get PDF text ready for LLM question extraction.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text suitable for LLM processing
    """
    text, _ = extract_pdf_text(pdf_path)
    return text


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pdf_parser_rag.py <pdf_path> [output_dir]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    success, out_dir = parse_pdf_simple(pdf_path, output_dir)
    
    if success:
        print(f"\n✓ Success! Output at: {out_dir}")
    else:
        print("\n✗ Failed to parse PDF")
        sys.exit(1)
