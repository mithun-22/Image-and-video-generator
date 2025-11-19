import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # File Processing
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    CHUNK_SIZE = 4000  # characters per chunk
    SUPPORTED_FORMATS = ['.txt', '.pdf', '.docx']
    
    # Directories
    BASE_DIR = Path(__file__).parent
    UPLOAD_DIR = BASE_DIR / "uploads"
    OUTPUT_DIR = BASE_DIR / "outputs"
    IMAGE_DIR = OUTPUT_DIR / "images"
    SUMMARY_DIR = OUTPUT_DIR / "summaries"
    
    # Image Generation
    IMAGE_WIDTH = 1024
    IMAGE_HEIGHT = 768
    IMAGE_QUALITY = 95
    
    @classmethod
    def setup_directories(cls):
        """Create necessary directories"""
        cls.UPLOAD_DIR.mkdir(exist_ok=True)
        cls.OUTPUT_DIR.mkdir(exist_ok=True)
        cls.IMAGE_DIR.mkdir(exist_ok=True)
        cls.SUMMARY_DIR.mkdir(exist_ok=True)
