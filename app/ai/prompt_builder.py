"""Prompt engineering and building module - now flexible for any type of question."""

from typing import Dict, List
from dataclasses import dataclass
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class GenerationRules:
    """Rules and constraints for code generation."""
    jwt_auth: bool = False
    crud_operations: bool = False
    user_model: bool = False
    database: bool = True
    custom_rules: List[str] = None

    def __post_init__(self):
        if self.custom_rules is None:
            self.custom_rules = []


class PromptBuilder:
    """Build flexible prompts for any type of coding assistance."""

    SYSTEM_PROMPT = """You are an expert coding assistant and Python developer.

Your capabilities:
- Answer programming questions
- Explain code and coding concepts  
- Generate code snippets and full applications
- Help with algorithms and data structures
- Explain complex code
- Answer any technical question
- Provide best practices and solutions

When responding:
1. Understand what the user is really asking
2. Provide clear, helpful answers
3. For code: output clean, working code
4. For questions: explain thoroughly
5. For explanations: break it down simply
6. Always provide production-ready solutions

Important:
- Be flexible - handle ANY type of request
- If simple code is requested, give just that code
- If full system is requested, structure it properly  
- Always make code syntactically correct and ready to use
- Use Python best practices
- No markdown formatting around code (unless asked)
- No unnecessary explanations (unless asked)"""

    @staticmethod
    def build_prompt(user_prompt: str, rules: GenerationRules = None) -> str:
        """
        Build a prompt for LLM.
        Now handles ANY type of request - code, questions, explanations.

        Args:
            user_prompt: User's request (can be anything)
            rules: Generation rules (optional, mostly ignored for flexibility)

        Returns:
            The user prompt (LLM is smart enough to understand context)
        """
        logger.info(f"Processing prompt: {user_prompt[:50]}...")
        return user_prompt

    @staticmethod
    def build_system_message() -> str:
        """Get the system message for the LLM."""
        return PromptBuilder.SYSTEM_PROMPT
