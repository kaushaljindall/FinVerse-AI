"""
FinVerse AI — Document Processor
Chunks documents for RAG ingestion. Supports text files for compliance docs.
"""

import os
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process and chunk documents for RAG pipeline."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def process_file(self, file_path: str) -> list[dict]:
        """
        Read and chunk a document file.
        Returns list of {text, metadata} chunks.
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return []

        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()

        if ext in [".txt", ".md"]:
            text = self._read_text(file_path)
        elif ext == ".pdf":
            text = self._read_pdf(file_path)
        else:
            logger.warning(f"Unsupported file type: {ext}")
            text = self._read_text(file_path)

        if not text:
            return []

        chunks = self._chunk_text(text)
        return [
            {
                "text": chunk,
                "metadata": {
                    "source": filename,
                    "file_path": file_path,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                },
            }
            for i, chunk in enumerate(chunks)
        ]

    def process_directory(self, directory: str) -> list[dict]:
        """Process all supported documents in a directory."""
        all_chunks = []
        if not os.path.exists(directory):
            logger.warning(f"Directory not found: {directory}")
            return all_chunks

        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                chunks = self.process_file(filepath)
                all_chunks.extend(chunks)
                logger.info(f"📄 Processed {filename}: {len(chunks)} chunks")

        return all_chunks

    def _read_text(self, file_path: str) -> str:
        """Read a text file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return ""

    def _read_pdf(self, file_path: str) -> str:
        """Read a PDF file using PyPDF2."""
        try:
            import PyPDF2
            text = ""
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except ImportError:
            logger.warning("PyPDF2 not installed, skipping PDF")
            return ""
        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {e}")
            return ""

    def _chunk_text(self, text: str) -> list[str]:
        """Split text into overlapping chunks by sentence boundaries."""
        # Clean text
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.strip()

        if len(text) <= self.chunk_size:
            return [text]

        # Split by sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)

        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += (" " if current_chunk else "") + sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks if chunks else [text[:self.chunk_size]]
