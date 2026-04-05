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
        Build a prompt for LLM with generation rules applied.

        Args:
            user_prompt: User's request (can be anything)
            rules: Generation rules to apply (optional)

        Returns:
            Enhanced prompt with rules included
        """
        logger.info(f"Processing prompt: {user_prompt[:50]}...")

        if rules is None:
            rules = GenerationRules()

        # Build requirements list
        requirements = []
        if rules.jwt_auth:
            requirements.append("- Include JWT authentication/authorization")
        if rules.crud_operations:
            requirements.append("- Include full CRUD operations")
        if rules.user_model:
            requirements.append("- Include user model and management")
        if rules.database:
            requirements.append("- Include database integration")
        if rules.custom_rules:
            requirements.extend([f"- {rule}" for rule in rules.custom_rules])

        # Build final prompt
        if requirements:
            requirements_text = "\n".join(requirements)
            enhanced_prompt = f"""{user_prompt}

Required features/rules:
{requirements_text}"""
            return enhanced_prompt

        return user_prompt

    @staticmethod
    def extract_requirements(prompt: str) -> GenerationRules:
        """
        Extract generation requirements from a prompt.

        Args:
            prompt: User prompt to analyze

        Returns:
            GenerationRules with extracted requirements
        """
        prompt_lower = prompt.lower()

        rules = GenerationRules(
            jwt_auth=(
                "jwt" in prompt_lower or
                "authentication" in prompt_lower or
                "auth" in prompt_lower
            ),
            crud_operations=(
                "crud" in prompt_lower or
                "create" in prompt_lower and "read" in prompt_lower or
                "update" in prompt_lower and "delete" in prompt_lower
            ),
            user_model=(
                "user" in prompt_lower and
                ("model" in prompt_lower or "management" in prompt_lower or "system" in prompt_lower)
            ),
            database=True,  # Default to database unless explicitly disabled
        )

        logger.info(f"Extracted requirements: jwt_auth={rules.jwt_auth}, crud={rules.crud_operations}, user_model={rules.user_model}")
        return rules

    @staticmethod
    def build_system_message() -> str:
        """Get the system message for the LLM."""
        return PromptBuilder.SYSTEM_PROMPT
