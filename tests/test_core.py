"""Basic tests for the API Builder."""

import pytest
from app.ai.prompt_builder import PromptBuilder, GenerationRules
from app.ai.parser import CodeParser, CodeBlock
from app.generator.cleaner import CodeCleaner
from app.generator.validator import CodeValidator


class TestPromptBuilder:
    """Test prompt building functionality."""

    def test_build_prompt_with_rules(self):
        """Test building a prompt with rules."""
        prompt = "Create a user API"
        rules = GenerationRules(jwt_auth=True, crud_operations=True)

        result = PromptBuilder.build_prompt(prompt, rules)

        assert "Create a user API" in result
        assert "JWT" in result or "jwt" in result.lower()
        assert "CRUD" in result or "crud" in result.lower()

    def test_extract_requirements_jwt(self):
        """Test requirement extraction for JWT."""
        prompt = "Create API with JWT authentication"
        rules = PromptBuilder.extract_requirements(prompt)

        assert rules.jwt_auth is True

    def test_extract_requirements_crud(self):
        """Test requirement extraction for CRUD."""
        prompt = "Build a CRUD API"
        rules = PromptBuilder.extract_requirements(prompt)

        assert rules.crud_operations is True

    def test_extract_requirements_user_model(self):
        """Test requirement extraction for user model."""
        prompt = "Create user management system"
        rules = PromptBuilder.extract_requirements(prompt)

        assert rules.user_model is True


class TestCodeParser:
    """Test code parsing functionality."""

    def test_parse_structured_output(self):
        """Test parsing structured code output."""
        output = """# models.py
from sqlalchemy import Column, Integer, String

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)

# schemas.py
from pydantic import BaseModel

class UserSchema(BaseModel):
    id: int
    name: str
"""

        blocks = CodeParser.parse_structured_output(output)

        assert len(blocks) == 2
        assert "models.py" in blocks
        assert "schemas.py" in blocks
        assert "User" in blocks["models.py"].content

    def test_parse_markdown_output(self):
        """Test parsing markdown code blocks."""
        output = """Some explanation text

```python
def hello():
    return "world"
```

More text

```python
def goodbye():
    return "world"
```
"""

        blocks = CodeParser.parse_markdown_output(output)

        assert len(blocks) >= 2

    def test_validate_parsed_blocks(self):
        """Test validation of parsed blocks."""
        blocks = {
            "models.py": CodeBlock(
                filename="models.py",
                content="class User: pass"
            )
        }

        result = CodeParser.validate_parsed_blocks(blocks)
        assert result is True

    def test_validate_empty_blocks(self):
        """Test validation with empty blocks."""
        blocks = {}

        result = CodeParser.validate_parsed_blocks(blocks)
        assert result is False


class TestCodeCleaner:
    """Test code cleaning functionality."""

    def test_remove_markdown(self):
        """Test markdown removal."""
        code = "```python\nprint('hello')\n```"

        cleaned = CodeCleaner.remove_markdown(code)

        assert "```" not in cleaned
        assert "print('hello')" in cleaned

    def test_fix_indentation(self):
        """Test indentation fixing."""
        code = "def func():\nreturn True"

        cleaned = CodeCleaner.fix_indentation(code)

        assert "return True" in cleaned

    def test_remove_trailing_whitespace(self):
        """Test trailing whitespace removal."""
        code = "print('hello')   \nprint('world')  "

        cleaned = CodeCleaner.remove_trailing_whitespace(code)

        assert not cleaned.split('\n')[0].endswith('   ')

    def test_ensure_newline_at_end(self):
        """Test newline at end of file."""
        code = "print('hello')"

        cleaned = CodeCleaner.ensure_newline_at_end(code)

        assert cleaned.endswith('\n')

    def test_clean_code_complete(self):
        """Test complete code cleaning."""
        code = "```python\ndef func( ):\n  return True   \n```"

        cleaned = CodeCleaner.clean_code(code)

        assert "```" not in cleaned
        assert cleaned.endswith('\n')


class TestCodeValidator:
    """Test code validation functionality."""

    def test_validate_syntax_valid(self):
        """Test validation of valid Python code."""
        code = "def hello():\n    return 'world'"

        result = CodeValidator.validate_syntax(code, "test.py")

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_syntax_invalid(self):
        """Test validation of invalid Python code."""
        code = "def hello(\n    return 'world'"

        result = CodeValidator.validate_syntax(code, "test.py")

        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_validate_security_safe(self):
        """Test security validation of safe code."""
        code = "import os\nprint('hello')"

        result = CodeValidator.validate_security(code, "test.py")

        assert result.is_valid is True

    def test_validate_security_unsafe(self):
        """Test security validation of unsafe code."""
        code = "os.system('rm -rf /')"

        result = CodeValidator.validate_security(code, "test.py")

        assert result.is_valid is False
        assert len(result.errors) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

