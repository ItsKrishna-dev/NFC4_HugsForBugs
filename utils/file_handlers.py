import os
import shutil
from pathlib import Path
from typing import Optional
from config.settings import UPLOAD_DIR

# Ensure upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_upload(file_obj, filename: Optional[str] = None) -> Path:
    """
    Save a Streamlit-uploaded file and return its path.

    Args:
        file_obj: Streamlit uploaded file object
        filename: Optional custom filename

    Returns:
        Path to saved file
    """
    if filename is None:
        filename = file_obj.name

    file_path = UPLOAD_DIR / filename

    # Handle duplicate filenames
    counter = 1
    original_path = file_path
    while file_path.exists():
        stem = original_path.stem
        suffix = original_path.suffix
        file_path = UPLOAD_DIR / f"{stem}_{counter}{suffix}"
        counter += 1

    # Save the file
    with open(file_path, "wb") as f:
        f.write(file_obj.getbuffer())

    return file_path


def cleanup_uploads(max_files: int = 100):
    """Clean up old uploaded files if too many exist."""
    upload_files = list(UPLOAD_DIR.glob("*"))
    if len(upload_files) > max_files:
        # Sort by modification time and remove oldest
        upload_files.sort(key=lambda x: x.stat().st_mtime)
        for old_file in upload_files[:-max_files]:
            old_file.unlink()


def get_file_size(file_path: Path) -> int:
    """Get file size in bytes."""
    return file_path.stat().st_size


def delete_file(file_path: Path) -> bool:
    """Safely delete a file."""
    try:
        file_path.unlink()
        return True
    except Exception:
        return False
