"""Custom exceptions for the API Builder application."""


class APIBuilderException(Exception):
    """Base exception for all API Builder errors."""
    pass


class OllamaException(APIBuilderException):
    """Raised when Ollama connection or API fails."""
    pass


class PromptValidationException(APIBuilderException):
    """Raised when prompt validation fails."""
    pass


class CodeValidationException(APIBuilderException):
    """Raised when generated code fails validation."""
    pass


class CodeParsingException(APIBuilderException):
    """Raised when parsing LLM output fails."""
    pass


class FileOperationException(APIBuilderException):
    """Raised when file operations fail."""
    pass


class ProjectNotFoundError(APIBuilderException):
    """Raised when a project cannot be found."""
    pass


class ExecutionException(APIBuilderException):
    """Raised when project execution fails."""
    pass

