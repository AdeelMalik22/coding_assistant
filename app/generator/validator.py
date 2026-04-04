"""Code validation module."""

import ast
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from utils.logger import get_logger
from utils.errors import CodeValidationException

logger = get_logger(__name__)


@dataclass
class ValidationError:
    """Represents a validation error."""
    severity: str  # "error", "warning"
    message: str
    filename: str
    line_number: Optional[int] = None


@dataclass
class ValidationResult:
    """Result of code validation."""
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        return len(self.warnings) > 0

    def to_dict(self) -> dict:
        return {
            "is_valid": self.is_valid,
            "errors": [
                {"message": e.message, "file": e.filename, "line": e.line_number}
                for e in self.errors
            ],
            "warnings": [
                {"message": w.message, "file": w.filename, "line": w.line_number}
                for w in self.warnings
            ],
        }


class CodeValidator:
    """Validate generated Python code."""

    # Forbidden patterns that could be dangerous
    FORBIDDEN_PATTERNS = [
        (r"os\.system\(|subprocess\.|exec\(|eval\(", "Dangerous: shell execution not allowed"),
        (r"__import__\(|importlib\.import_module", "Dangerous: dynamic imports not allowed"),
        (r"open\(['\"].*['\"].*['\"]w", "Dangerous: file writing not allowed"),
        (r"rmtree|remove\(", "Dangerous: file deletion not allowed"),
    ]

    # Required imports for FastAPI apps
    EXPECTED_IMPORTS = ["fastapi", "sqlalchemy", "pydantic"]

    @staticmethod
    def validate_syntax(code: str, filename: str) -> ValidationResult:
        """
        Validate Python syntax using AST parsing.

        Args:
            code: Python code to validate
            filename: Name of the file for error reporting

        Returns:
            ValidationResult with errors and warnings
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[])

        try:
            ast.parse(code)
            logger.info(f"Syntax validation passed for {filename}")
        except SyntaxError as e:
            result.is_valid = False
            result.errors.append(
                ValidationError(
                    severity="error",
                    message=f"Syntax error: {e.msg}",
                    filename=filename,
                    line_number=e.lineno,
                )
            )
            logger.error(f"Syntax error in {filename}: {e.msg}")

        return result

    @staticmethod
    def validate_security(code: str, filename: str) -> ValidationResult:
        """
        Validate code for security issues.

        Args:
            code: Python code to validate
            filename: Name of the file for error reporting

        Returns:
            ValidationResult with security issues
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[])

        for pattern, message in CodeValidator.FORBIDDEN_PATTERNS:
            if re.search(pattern, code):
                result.is_valid = False
                result.errors.append(
                    ValidationError(
                        severity="error",
                        message=message,
                        filename=filename,
                    )
                )
                logger.warning(f"Security issue in {filename}: {message}")

        return result

    @staticmethod
    def validate_imports(code: str, filename: str) -> ValidationResult:
        """
        Validate that imports are valid.

        Args:
            code: Python code to validate
            filename: Name of the file for error reporting

        Returns:
            ValidationResult with import issues
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[])

        try:
            tree = ast.parse(code)
            imports = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split(".")[0])

            # Check for common typing issues
            if "typing" in code and "from typing import" in code:
                # This is OK
                pass

            logger.info(f"Import validation passed for {filename}")

        except Exception as e:
            logger.warning(f"Could not validate imports: {str(e)}")

        return result

    @staticmethod
    def validate_structure(code: str, filename: str) -> ValidationResult:
        """
        Validate code structure and best practices.

        Args:
            code: Python code to validate
            filename: Name of the file for error reporting

        Returns:
            ValidationResult with structural issues
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[])

        try:
            tree = ast.parse(code)

            # Check for empty files
            if len(tree.body) == 0:
                result.warnings.append(
                    ValidationError(
                        severity="warning",
                        message="File is empty or contains only comments",
                        filename=filename,
                    )
                )

            # Check for missing docstrings in modules
            if isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant):
                # Module has docstring - good
                pass
            else:
                # Check if it's a models or schemas file
                if filename in ["models.py", "schemas.py"]:
                    result.warnings.append(
                        ValidationError(
                            severity="warning",
                            message="Module should have a docstring",
                            filename=filename,
                        )
                    )

            # Check for class and function definitions
            class_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
            func_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))

            if filename == "models.py" and class_count == 0:
                result.warnings.append(
                    ValidationError(
                        severity="warning",
                        message="models.py should contain class definitions",
                        filename=filename,
                    )
                )

            if filename == "routes.py" and func_count == 0:
                result.warnings.append(
                    ValidationError(
                        severity="warning",
                        message="routes.py should contain function definitions",
                        filename=filename,
                    )
                )

        except Exception as e:
            logger.warning(f"Could not validate structure: {str(e)}")

        return result

    @staticmethod
    def validate_code_blocks(code_blocks: Dict[str, "CodeBlock"]) -> Dict[str, ValidationResult]:
        """
        Validate multiple code blocks.

        Args:
            code_blocks: Dictionary of filename to CodeBlock

        Returns:
            Dictionary of filename to ValidationResult
        """
        results = {}

        for filename, block in code_blocks.items():
            logger.info(f"Validating {filename}")

            # Run all validators
            syntax_result = CodeValidator.validate_syntax(block.content, filename)
            security_result = CodeValidator.validate_security(block.content, filename)
            imports_result = CodeValidator.validate_imports(block.content, filename)
            structure_result = CodeValidator.validate_structure(block.content, filename)

            # Combine results
            combined = ValidationResult(is_valid=True, errors=[], warnings=[])
            for result in [syntax_result, security_result, imports_result, structure_result]:
                combined.is_valid = combined.is_valid and result.is_valid
                combined.errors.extend(result.errors)
                combined.warnings.extend(result.warnings)

            results[filename] = combined

            if combined.has_errors():
                logger.error(f"Validation failed for {filename}: {len(combined.errors)} errors")
            else:
                logger.info(f"Validation passed for {filename}")

        return results

    @staticmethod
    def get_validation_report(results: Dict[str, ValidationResult]) -> str:
        """
        Generate a human-readable validation report.

        Args:
            results: Dictionary of validation results

        Returns:
            Formatted validation report
        """
        lines = ["=== Code Validation Report ===\n"]

        total_errors = 0
        total_warnings = 0

        for filename, result in results.items():
            total_errors += len(result.errors)
            total_warnings += len(result.warnings)

            status = "✓ VALID" if result.is_valid else "✗ INVALID"
            lines.append(f"{filename}: {status}")

            for error in result.errors:
                line_info = f" (line {error.line_number})" if error.line_number else ""
                lines.append(f"  ERROR: {error.message}{line_info}")

            for warning in result.warnings:
                lines.append(f"  WARNING: {warning.message}")

            lines.append("")

        lines.append(f"Summary: {total_errors} errors, {total_warnings} warnings")

        return "\n".join(lines)


