"""LLM output parsing module."""

import re
import json
from dataclasses import dataclass
from typing import Dict, List, Optional
from utils.logger import get_logger
from utils.errors import CodeParsingException

logger = get_logger(__name__)


@dataclass
class CodeBlock:
    """Represents a parsed code block."""
    filename: str
    content: str
    language: str = "python"

    def __repr__(self):
        return f"CodeBlock(filename='{self.filename}', lines={len(self.content.splitlines())})"


class CodeParser:
    """Parse and extract code blocks from LLM output."""

    # Pattern to match labeled code sections like "# models.py"
    SECTION_PATTERN = r"^#\s*(\w+\.py)\s*$"

    # Pattern to match markdown code blocks
    MARKDOWN_PATTERN = r"```(?:python)?\n(.*?)\n```"

    @staticmethod
    def parse_structured_output(output: str) -> Dict[str, CodeBlock]:
        """
        Parse structured LLM output with labeled sections.

        Expected format:
        # models.py
        <code>

        # schemas.py
        <code>

        # routes.py
        <code>

        Args:
            output: Raw LLM output

        Returns:
            Dictionary mapping filename to CodeBlock

        Raises:
            CodeParsingException: If parsing fails
        """
        if not output or not output.strip():
            raise CodeParsingException("Empty LLM output received")

        code_blocks = {}
        lines = output.split("\n")
        current_filename = None
        current_code = []

        for line in lines:
            # Check if this is a section header
            match = re.match(CodeParser.SECTION_PATTERN, line.strip())
            if match:
                # Save previous section if exists
                if current_filename and current_code:
                    code_content = "\n".join(current_code).strip()
                    if code_content:
                        code_blocks[current_filename] = CodeBlock(
                            filename=current_filename,
                            content=code_content
                        )

                # Start new section
                current_filename = match.group(1)
                current_code = []
                logger.info(f"Parsing section: {current_filename}")
            elif current_filename is not None:
                # Add line to current code block
                current_code.append(line)

        # Save last section
        if current_filename and current_code:
            code_content = "\n".join(current_code).strip()
            if code_content:
                code_blocks[current_filename] = CodeBlock(
                    filename=current_filename,
                    content=code_content
                )

        if not code_blocks:
            raise CodeParsingException("No code blocks found in LLM output")

        logger.info(f"Successfully parsed {len(code_blocks)} code blocks")
        return code_blocks

    @staticmethod
    def parse_markdown_output(output: str) -> Dict[str, CodeBlock]:
        """
        Parse LLM output with markdown code blocks.

        Expected format:
        ```python
        <code>
        ```

        Args:
            output: Raw LLM output with markdown blocks

        Returns:
            Dictionary mapping generated filenames to CodeBlock

        Raises:
            CodeParsingException: If parsing fails
        """
        if not output or not output.strip():
            raise CodeParsingException("Empty LLM output received")

        # Find all markdown code blocks
        matches = re.finditer(CodeParser.MARKDOWN_PATTERN, output, re.DOTALL)
        code_blocks = {}
        block_index = 0

        for match in matches:
            code_content = match.group(1).strip()
            if not code_content:
                continue

            # Try to infer filename from code content
            filename = CodeParser._infer_filename(code_content)
            if not filename:
                filename = f"generated_{block_index}.py"
                block_index += 1

            code_blocks[filename] = CodeBlock(
                filename=filename,
                content=code_content
            )
            logger.info(f"Extracted code block: {filename}")

        if not code_blocks:
            raise CodeParsingException("No markdown code blocks found in output")

        return code_blocks

    @staticmethod
    def _infer_filename(code_content: str) -> Optional[str]:
        """
        Try to infer filename from code content patterns.

        Args:
            code_content: Python code content

        Returns:
            Inferred filename or None
        """
        # Check for model definitions
        if re.search(r"class\s+\w+\(Base\)", code_content):
            return "models.py"

        # Check for Pydantic schemas
        if re.search(r"class\s+\w+\(BaseModel\)", code_content):
            return "schemas.py"

        # Check for route definitions
        if re.search(r"@app\.|@router\.", code_content):
            return "routes.py"

        # Check for views
        if re.search(r"def\s+\w+\(.*request.*\):", code_content):
            return "views.py"

        # Check for database
        if re.search(r"engine|SessionLocal|Base\.metadata", code_content):
            return "database.py"

        return None

    @staticmethod
    def parse_response(output: str) -> Dict[str, CodeBlock]:
        """
        Automatically detect and parse LLM output format.
        Handles both code and plain text responses.

        Args:
            output: Raw LLM output (can be code or text)

        Returns:
            Dictionary mapping filename to CodeBlock

        Raises:
            CodeParsingException: If no valid format found
        """
        # Try structured format first
        try:
            if re.search(CodeParser.SECTION_PATTERN, output, re.MULTILINE):
                return CodeParser.parse_structured_output(output)
        except CodeParsingException:
            pass

        # Try markdown format
        try:
            if "```" in output:
                return CodeParser.parse_markdown_output(output)
        except CodeParsingException:
            pass

        # If not code, treat as plain text response (questions, explanations, etc)
        logger.info("Output is plain text (not structured code)")
        return {
            "response.txt": CodeBlock(
                filename="response.txt",
                content=output.strip(),
                language="text"
            )
        }

    @staticmethod
    def validate_parsed_blocks(code_blocks: Dict[str, CodeBlock]) -> bool:
        """
        Validate parsed code blocks for basic sanity checks.

        Args:
            code_blocks: Parsed code blocks

        Returns:
            True if valid, False otherwise
        """
        if not code_blocks:
            logger.warning("No code blocks to validate")
            return False

        for filename, block in code_blocks.items():
            # Check content is not empty
            if not block.content or not block.content.strip():
                logger.warning(f"Code block {filename} is empty")
                return False

            # Check filename is valid
            if not re.match(r"^[\w.-]+\.py$", filename):
                logger.warning(f"Invalid filename: {filename}")
                return False

        logger.info(f"Successfully validated {len(code_blocks)} code blocks")
        return True

