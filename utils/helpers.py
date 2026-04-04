"""Utility functions for the API Builder."""

import uuid
import re
from datetime import datetime
from pathlib import Path


def generate_project_id() -> str:
    """Generate a unique project ID."""
    return f"project_{uuid.uuid4().hex[:12]}"


def generate_timestamp() -> str:
    """Generate an ISO format timestamp."""
    return datetime.utcnow().isoformat()


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to prevent directory traversal attacks."""
    # Remove any directory separators
    filename = filename.replace("../", "").replace("..\\", "")
    # Remove any path separators at the start
    filename = filename.lstrip("/\\")
    # Replace unsafe characters
    filename = re.sub(r"[^\w\s.-]", "", filename)
    return filename


def ensure_directory(path: Path) -> Path:
    """Ensure directory exists and return the path."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_read_file(filepath: Path, encoding: str = "utf-8") -> str:
    """Safely read a file with error handling."""
    try:
        return filepath.read_text(encoding=encoding)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
    except Exception as e:
        raise Exception(f"Error reading file {filepath}: {str(e)}")


def safe_write_file(filepath: Path, content: str, encoding: str = "utf-8") -> None:
    """Safely write to a file with error handling."""
    try:
        # Ensure parent directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content, encoding=encoding)
    except Exception as e:
        raise Exception(f"Error writing to file {filepath}: {str(e)}")

