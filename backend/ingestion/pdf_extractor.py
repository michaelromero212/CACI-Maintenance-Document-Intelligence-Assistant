"""PDF text extraction using pdfplumber."""

import pdfplumber
from io import BytesIO
from typing import Optional


class PDFExtractor:
    """Extract text content from PDF documents."""
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract all text from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text content
        """
        text_parts = []
        
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        
        return "\n\n".join(text_parts)
    
    def extract_text_from_bytes(self, content: bytes) -> str:
        """
        Extract text from PDF bytes.
        
        Args:
            content: PDF file content as bytes
            
        Returns:
            Extracted text content
        """
        text_parts = []
        
        with pdfplumber.open(BytesIO(content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        
        return "\n\n".join(text_parts)
    
    def extract_tables(self, file_path: str) -> list:
        """
        Extract tables from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of tables (each table is a list of rows)
        """
        tables = []
        
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)
        
        return tables
