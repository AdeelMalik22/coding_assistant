import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""

    # Ollama Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
    OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "120"))
    OLLAMA_FALLBACK_MODEL: str = os.getenv("OLLAMA_FALLBACK_MODEL", "qwen2.5-coder:3b")

    # Application Settings
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    MAX_PROMPT_SIZE: int = int(os.getenv("MAX_PROMPT_SIZE", "2000"))

    # File Paths
    PROJECT_ROOT = Path(__file__).parent.parent
    GENERATED_PROJECTS_DIR: Path = Path(os.getenv("GENERATED_PROJECTS_DIR", "./generated_projects"))
    TEMPLATES_DIR: Path = PROJECT_ROOT / "app" / "templates"
    STATIC_DIR: Path = PROJECT_ROOT / "app" / "static"

    # Validation Settings
    MAX_FILE_SIZE: int = 500000  # 500KB
    ALLOWED_EXTENSIONS: set = {"py", "txt", "json", "yaml", "yml"}

    # FastAPI Settings
    API_TITLE: str = "AI-Powered API Builder"
    API_VERSION: str = "0.1.0"
    API_DESCRIPTION: str = "Generate FastAPI backends from natural language prompts using Ollama"

# Create singleton instance
settings = Settings()

# Ensure generated projects directory exists
settings.GENERATED_PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

