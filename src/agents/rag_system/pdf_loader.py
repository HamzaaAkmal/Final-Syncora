"""
PDF Loader & Chunker
====================

Handles PDF upload, extraction, and chunking for RAG system.
"""

import os
from pathlib import Path
from typing import List, Dict, Any
import PyPDF2

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter


class PDFLoader:
    """Load and chunk PDF documents."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        """
        Initialize PDF loader.
        
        Args:
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        self.uploaded_pdfs = {}
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                num_pages = len(reader.pages)
                
                for page_num in range(num_pages):
                    page = reader.pages[page_num]
                    text += f"\n--- Page {page_num + 1} ---\n"
                    text += page.extract_text()
            
            return text
        except Exception as e:
            raise ValueError(f"Error extracting PDF: {str(e)}")
    
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Split text into chunks.
        
        Args:
            text: Text to chunk
            metadata: Additional metadata
            
        Returns:
            List of chunks with metadata
        """
        chunks = self.text_splitter.split_text(text)
        
        result = []
        for i, chunk in enumerate(chunks):
            result.append({
                "content": chunk,
                "chunk_id": i,
                "metadata": metadata or {}
            })
        
        return result
    
    def process_pdf(self, pdf_path: str, pdf_name: str = None) -> List[Dict[str, Any]]:
        """
        Complete PDF processing: extract + chunk.
        
        Args:
            pdf_path: Path to PDF
            pdf_name: Name for tracking
            
        Returns:
            List of chunks
        """
        pdf_name = pdf_name or Path(pdf_path).stem
        
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        
        # Chunk text
        chunks = self.chunk_text(
            text,
            metadata={
                "source": pdf_name,
                "file_path": pdf_path,
                "total_text_length": len(text)
            }
        )
        
        # Store reference
        self.uploaded_pdfs[pdf_name] = {
            "path": pdf_path,
            "num_chunks": len(chunks),
            "text_length": len(text)
        }
        
        return chunks
    
    def get_pdf_info(self) -> Dict[str, Dict]:
        """Get information about uploaded PDFs."""
        return self.uploaded_pdfs
