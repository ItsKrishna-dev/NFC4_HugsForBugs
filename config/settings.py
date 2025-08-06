import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
PROCESSED_DIR = DATA_DIR / "processed"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"

# Create directories
for dir_path in [DATA_DIR, UPLOAD_DIR, PROCESSED_DIR, EMBEDDINGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Processing settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Model settings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
SUMMARIZATION_MODEL = "t5-small"

# Cache settings
CACHE_RETENTION_DAYS = 30
MAX_CACHE_SIZE_GB = 5

# Supported formats
SUPPORTED_FORMATS = {'.pdf', '.docx', '.txt', '.md', '.rtf'}

# Database settings
DATABASE_URL = f"sqlite:///{PROCESSED_DIR}/metadata.db"
