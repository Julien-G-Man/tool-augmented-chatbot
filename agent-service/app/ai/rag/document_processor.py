"""
Document Processor Module

Handles converting raw PDFs into chunks ready for embedding.
Extracts text from PDFs and splits into manageable pieces.

Learning Goal: RAG works better with chunked text. Too small = loses context.
Too large = dilutes relevance. ~500 tokens with overlap is a good balance.
"""

from typing import List, Dict, Any
import os
import re
from pathlib import Path
from pypdf import PdfReader


class DocumentChunk:
    """Represents a chunk of a document."""
    
    def __init__(
        self,
        content: str,
        source_file: str,
        chunk_index: int,
        metadata: Dict[str, Any] = None
    ):
        """
        Initialize a document chunk.
        
        Args:
            content: The actual text content
            source_file: Name of source PDF file
            chunk_index: Which chunk this is (0-indexed)
            metadata: Additional info (page number, date, etc.)
        """
        self.content = content
        self.source_file = source_file
        self.chunk_index = chunk_index
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "content": self.content,
            "source_file": self.source_file,
            "chunk_index": self.chunk_index,
            "metadata": self.metadata,
        }


class DocumentProcessor:
    """
    Process PDFs and split into chunks.
    
    Pipeline:
    1. Read PDF file
    2. Extract text
    3. Split into chunks
    4. Add metadata
    
    Note: This uses placeholder implementation.
    In production, use PyPDF2, pdfplumber, or Unstructured.io
    """
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize document processor.
        
        Args:
            chunk_size: Target size of each chunk in tokens
                       ~4 chars = 1 token, so 500 tokens ≈ 2000 chars
            chunk_overlap: Characters to repeat between chunks
                          Helps maintain context across boundaries
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process_pdf(self, pdf_path: str) -> List[DocumentChunk]:
        """
        Process a PDF file into chunks.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of DocumentChunk objects
        """
        # Check file exists
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        # Extract text from PDF using a proper PDF parser.
        text = self._extract_text(pdf_path)
        
        # Get filename without path
        filename = Path(pdf_path).name
        
        # Split into chunks
        chunks = self._split_text(text, filename)
        
        return chunks

    def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF/TXT files and normalize for chunking."""
        suffix = Path(file_path).suffix.lower()

        if suffix == ".pdf":
            return self._extract_pdf_text(file_path)
        if suffix == ".txt":
            return self._extract_txt_text(file_path)

        raise ValueError(f"Unsupported file type: {suffix}")

    def _extract_pdf_text(self, pdf_path: str) -> str:
        """Extract PDF text page-by-page with normalization."""
        try:
            reader = PdfReader(pdf_path)
        except Exception as exc:
            raise ValueError(f"Could not open PDF: {pdf_path}") from exc

        page_texts: List[str] = []
        for page in reader.pages:
            raw = page.extract_text() or ""
            cleaned = self._normalize_text(raw)
            if cleaned:
                page_texts.append(cleaned)

        text = "\n\n".join(page_texts).strip()
        if not text:
            raise ValueError(
                f"No readable text extracted from PDF: {pdf_path}. "
                "If this is a scanned PDF, OCR is required."
            )
        return text

    def _extract_txt_text(self, txt_path: str) -> str:
        """Extract text from plain text files."""
        try:
            with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
                raw = f.read()
        except Exception as exc:
            raise ValueError(f"Could not read text file: {txt_path}") from exc

        text = self._normalize_text(raw)
        if not text:
            raise ValueError(f"No readable text extracted from file: {txt_path}")
        return text

    def _normalize_text(self, text: str) -> str:
        """Normalize extracted text and drop common PDF extraction artifacts."""
        if not text:
            return ""

        normalized = text.replace("\x00", " ")
        normalized = re.sub(r"[\t\r\f\v]+", " ", normalized)
        normalized = re.sub(r"\u00ad", "", normalized)  # soft hyphen

        # Collapse whitespace and remove very noisy lines.
        lines = []
        for line in normalized.split("\n"):
            clean_line = re.sub(r"\s+", " ", line).strip()
            if not clean_line:
                continue
            if self._is_noise_line(clean_line):
                continue
            lines.append(clean_line)

        return "\n".join(lines).strip()

    @staticmethod
    def _is_noise_line(line: str) -> bool:
        """Heuristic to filter lines that are mostly non-language artifacts."""
        if len(line) < 4:
            return True

        alpha_count = sum(ch.isalpha() for ch in line)
        ratio = alpha_count / max(len(line), 1)
        if ratio < 0.2:
            return True

        if " Tj" in line or " ET" in line or " BT" in line:
            return True

        return False
    
    def _split_text(self, text: str, source_file: str) -> List[DocumentChunk]:
        """
        Split text into overlapping chunks.
        
        Why overlap? So concepts that span chunk boundaries
        aren't split across separate chunks.
        
        Example with overlap=50:
        Chunk 1: [0:500]
        Chunk 2: [450:950]  (overlaps last 50 chars)
        Chunk 3: [900:1400]
        """
        chunks = []
        chunk_size_chars = self.chunk_size * 4  # Rough estimate: 4 chars per token
        chunk_overlap_chars = self.chunk_overlap * 4
        
        start = 0
        chunk_index = 0
        
        while start < len(text):
            # Extract chunk
            end = min(start + chunk_size_chars, len(text))
            chunk_text = text[start:end].strip()
            
            if chunk_text:  # Only add non-empty chunks
                chunk = DocumentChunk(
                    content=chunk_text,
                    source_file=source_file,
                    chunk_index=chunk_index,
                    metadata={
                        "start_char": start,
                        "end_char": end,
                    }
                )
                chunks.append(chunk)
                chunk_index += 1
            
            # Move start position for next chunk
            # Move by chunk_size, but then back-up by overlap
            start = end - chunk_overlap_chars
            
            # Prevent infinite loop on small texts
            if end == len(text):
                break
        
        return chunks
    
    def process_directory(self, directory: str) -> List[DocumentChunk]:
        """
        Process all PDFs in a directory.
        
        Args:
            directory: Path to directory containing PDFs
            
        Returns:
            Combined list of chunks from all PDFs
        """
        all_chunks = []
        
        # Find all PDF files
        pdf_files = []
        for ext in ['*.pdf', '*.txt']:  # Support both PDF and text files
            pdf_files.extend(Path(directory).glob(ext))
        
        for pdf_path in pdf_files:
            try:
                print(f"Processing: {pdf_path}")
                chunks = self.process_pdf(str(pdf_path))
                all_chunks.extend(chunks)
                print(f"  -> Generated {len(chunks)} chunks")
            except Exception as e:
                print(f"  -> Error: {e}")
        
        return all_chunks
