"""Code cleaning and formatting module."""

import re
from typing import Dict, List
from utils.logger import get_logger

logger = get_logger(__name__)


class CodeCleaner:
    """Clean and format generated code."""

    @staticmethod
    def remove_markdown(code: str) -> str:
        """
        Remove markdown formatting from code.

        Args:
            code: Code potentially with markdown formatting

        Returns:
            Clean code without markdown
        """
        # Remove triple backticks and language identifier
        code = re.sub(r"```(?:python)?\n?", "", code)
        code = re.sub(r"\n?```", "", code)

        return code.strip()

    @staticmethod
    def fix_indentation(code: str) -> str:
        """
        Fix indentation issues in code.

        Args:
            code: Code with potential indentation issues

        Returns:
            Code with consistent indentation (4 spaces)
        """
        lines = code.split("\n")
        fixed_lines = []

        for line in lines:
            # Skip empty lines
            if not line.strip():
                fixed_lines.append("")
                continue

            # Calculate current indentation
            stripped = line.lstrip()
            old_indent = len(line) - len(stripped)

            # If using tabs, convert to spaces
            if "\t" in line[:old_indent]:
                indent_count = line[:old_indent].count("\t") * 4
                indent_count += line[:old_indent].count(" ")
                fixed_lines.append(" " * indent_count + stripped)
            else:
                fixed_lines.append(line)

        return "\n".join(fixed_lines)

    @staticmethod
    def remove_trailing_whitespace(code: str) -> str:
        """
        Remove trailing whitespace from lines.

        Args:
            code: Code with potential trailing whitespace

        Returns:
            Code without trailing whitespace
        """
        lines = code.split("\n")
        return "\n".join(line.rstrip() for line in lines)

    @staticmethod
    def ensure_newline_at_end(code: str) -> str:
        """
        Ensure file ends with a newline.

        Args:
            code: Code content

        Returns:
            Code ending with newline
        """
        if not code.endswith("\n"):
            return code + "\n"
        return code

    @staticmethod
    def remove_duplicate_imports(code: str) -> str:
        """
        Remove duplicate import statements.

        Args:
            code: Code with potential duplicate imports

        Returns:
            Code with unique imports
        """
        lines = code.split("\n")
        seen_imports = set()
        result = []
        import_section = []
        in_imports = True

        for line in lines:
            stripped = line.strip()

            # Check if this is an import line
            if stripped.startswith(("import ", "from ")):
                if stripped not in seen_imports:
                    seen_imports.add(stripped)
                    import_section.append(line)
                # Skip duplicate imports
            else:
                # End of import section
                if in_imports and import_section:
                    result.extend(import_section)
                    import_section = []
                    in_imports = False
                result.append(line)

        # Add remaining imports
        if import_section:
            result.extend(import_section)

        return "\n".join(result)

    @staticmethod
    def clean_code(code: str) -> str:
        """
        Apply all cleaning operations to code.

        Args:
            code: Raw code to clean

        Returns:
            Cleaned code
        """
        logger.info("Starting code cleaning process")

        # Remove markdown formatting
        code = CodeCleaner.remove_markdown(code)

        # Fix indentation
        code = CodeCleaner.fix_indentation(code)

        # Remove trailing whitespace
        code = CodeCleaner.remove_trailing_whitespace(code)

        # Remove duplicate imports
        code = CodeCleaner.remove_duplicate_imports(code)

        # Ensure file ends with newline
        code = CodeCleaner.ensure_newline_at_end(code)

        logger.info("Code cleaning completed")
        return code

    @staticmethod
    def clean_code_blocks(code_blocks: Dict[str, "CodeBlock"]) -> Dict[str, "CodeBlock"]:
        """
        Clean multiple code blocks.

        Args:
            code_blocks: Dictionary of filename to CodeBlock

        Returns:
            Dictionary of filename to cleaned CodeBlock
        """
        cleaned = {}

        for filename, block in code_blocks.items():
            logger.info(f"Cleaning {filename}")
            cleaned_content = CodeCleaner.clean_code(block.content)

            # Create new CodeBlock with cleaned content
            from app.ai.parser import CodeBlock
            cleaned[filename] = CodeBlock(
                filename=filename,
                content=cleaned_content,
                language=block.language
            )

        return cleaned

