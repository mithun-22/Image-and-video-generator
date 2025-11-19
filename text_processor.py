import PyPDF2
from docx import Document
import re
from pathlib import Path
from typing import List, Dict, Optional
import json


class TextExtractor:
    """Extract text from various file formats"""
    
    @staticmethod
    def extract_from_txt(file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
    
    @staticmethod
    def extract_from_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n\n"
            return text
        except Exception as e:
            raise Exception(f"Error extracting PDF: {str(e)}")
    
    @staticmethod
    def extract_from_docx(file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            raise Exception(f"Error extracting DOCX: {str(e)}")
    
    @classmethod
    def extract(cls, file_path: str) -> str:
        """Extract text based on file extension"""
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension == '.txt':
            return cls.extract_from_txt(file_path)
        elif extension == '.pdf':
            return cls.extract_from_pdf(file_path)
        elif extension == '.docx':
            return cls.extract_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {extension}")


class TextProcessor:
    """Process and clean extracted text"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,;:!?-]', '', text)
        # Remove multiple newlines
        text = re.sub(r'\n+', '\n', text)
        return text.strip()
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 4000, overlap: int = 200) -> List[str]:
        """
        Split text into chunks with overlap for context preservation
        
        Args:
            text: Input text to chunk
            chunk_size: Maximum characters per chunk
            overlap: Number of characters to overlap between chunks
        """
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 for space
            
            if current_length + word_length > chunk_size:
                # Save current chunk
                chunk_text = ' '.join(current_chunk)
                chunks.append(chunk_text)
                
                # Start new chunk with overlap
                overlap_words = []
                overlap_length = 0
                for w in reversed(current_chunk):
                    if overlap_length + len(w) + 1 <= overlap:
                        overlap_words.insert(0, w)
                        overlap_length += len(w) + 1
                    else:
                        break
                
                current_chunk = overlap_words + [word]
                current_length = sum(len(w) + 1 for w in current_chunk)
            else:
                current_chunk.append(word)
                current_length += word_length
        
        # Add final chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    @staticmethod
    def get_text_stats(text: str) -> Dict:
        """Get statistics about the text"""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        
        return {
            "total_characters": len(text),
            "total_words": len(words),
            "total_sentences": len([s for s in sentences if s.strip()]),
            "avg_word_length": sum(len(w) for w in words) / len(words) if words else 0,
            "avg_sentence_length": len(words) / len(sentences) if sentences else 0
        }
