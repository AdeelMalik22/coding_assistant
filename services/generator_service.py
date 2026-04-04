"""Generator service that orchestrates the entire code generation pipeline."""

from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

from utils.logger import get_logger
from utils.errors import APIBuilderException
from app.ai.llm import OllamaClient
from app.ai.prompt_builder import PromptBuilder, GenerationRules
from app.ai.parser import CodeParser
from app.generator.cleaner import CodeCleaner
from app.generator.validator import CodeValidator, ValidationResult
from app.generator.file_writer import FileWriter
from config.settings import settings

logger = get_logger(__name__)


@dataclass
class GenerationResult:
    """Result of code generation process."""
    project_id: str
    project_dir: Path
    code_blocks: Dict
    validation_results: Dict[str, ValidationResult]
    metadata: Dict
    success: bool
    error_message: Optional[str] = None


class GeneratorService:
    """Service for orchestrating the entire code generation pipeline."""

    def __init__(self, ollama_client: Optional[OllamaClient] = None):
        """
        Initialize the generator service.

        Args:
            ollama_client: Optional OllamaClient instance
        """
        self.ollama_client = ollama_client
        self.logger = get_logger(__name__)

    async def generate_api(
        self,
        user_prompt: str,
        rules: Optional[GenerationRules] = None,
        project_id: Optional[str] = None,
    ) -> GenerationResult:
        """
        Generate a complete FastAPI project from user prompt.

        Args:
            user_prompt: User's natural language request
            rules: Optional generation rules (auto-detected if not provided)
            project_id: Optional project ID (generated if not provided)

        Returns:
            GenerationResult with success status and details
        """
        logger.info(f"Starting code generation for prompt: {user_prompt[:100]}...")

        try:
            # Step 1: Auto-detect rules if not provided
            if rules is None:
                rules = PromptBuilder.extract_requirements(user_prompt)
                logger.info(f"Auto-detected rules: {rules}")

            # Step 2: Build engineered prompt
            engineered_prompt = PromptBuilder.build_prompt(user_prompt, rules)
            logger.info("Built engineered prompt")

            # Step 3: Generate code using Ollama
            if not self.ollama_client:
                self.ollama_client = OllamaClient()

            logger.info("Sending prompt to Ollama...")
            llm_response = await self.ollama_client.generate(engineered_prompt)
            logger.info(f"Received LLM response ({len(llm_response)} chars)")

            # Step 4: Parse LLM output
            logger.info("Parsing LLM output...")
            code_blocks = CodeParser.parse_response(llm_response)
            logger.info(f"Parsed {len(code_blocks)} code blocks")

            # Step 5: Clean code
            logger.info("Cleaning generated code...")
            cleaned_blocks = CodeCleaner.clean_code_blocks(code_blocks)
            logger.info("Code cleaning completed")

            # Step 6: Validate code
            logger.info("Validating generated code...")
            validation_results = CodeValidator.validate_code_blocks(cleaned_blocks)

            # Check if all blocks are valid
            has_errors = any(result.has_errors() for result in validation_results.values())
            if has_errors:
                error_report = CodeValidator.get_validation_report(validation_results)
                logger.warning(f"Validation issues found:\n{error_report}")

            # Step 7: Create project structure
            logger.info("Creating project structure...")
            project_dir = FileWriter.create_project_structure(project_id, include_defaults=True)

            # Step 8: Write code files
            logger.info("Writing code files...")
            written_files = FileWriter.write_code_blocks(project_dir, cleaned_blocks)
            logger.info(f"Written {len(written_files)} files")

            # Step 9: Write project metadata
            metadata = {
                "original_prompt": user_prompt,
                "rules": {
                    "jwt_auth": rules.jwt_auth,
                    "crud_operations": rules.crud_operations,
                    "user_model": rules.user_model,
                    "database": rules.database,
                    "custom_rules": rules.custom_rules,
                },
                "files_generated": list(written_files.keys()),
                "validation_summary": {
                    filename: {
                        "is_valid": result.is_valid,
                        "errors": len(result.errors),
                        "warnings": len(result.warnings),
                    }
                    for filename, result in validation_results.items()
                },
            }

            FileWriter.write_project_metadata(project_dir, user_prompt, metadata["rules"])

            logger.info(f"Successfully generated project: {project_dir}")

            return GenerationResult(
                project_id=project_dir.name,
                project_dir=project_dir,
                code_blocks=cleaned_blocks,
                validation_results=validation_results,
                metadata=metadata,
                success=not has_errors,
            )

        except Exception as e:
            logger.error(f"Code generation failed: {str(e)}", exc_info=True)
            return GenerationResult(
                project_id=project_id or "error",
                project_dir=Path(),
                code_blocks={},
                validation_results={},
                metadata={},
                success=False,
                error_message=str(e),
            )

    def get_project_info(self, project_id: str) -> Dict:
        """
        Get information about a generated project.

        Args:
            project_id: Project ID

        Returns:
            Dictionary with project information
        """
        project_dir = settings.GENERATED_PROJECTS_DIR / project_id

        if not project_dir.exists():
            raise FileNotFoundError(f"Project not found: {project_id}")

        import json

        # Read metadata
        metadata_file = project_dir / ".project_metadata.json"
        metadata = {}
        if metadata_file.exists():
            metadata = json.loads(metadata_file.read_text())

        # Get all files
        files = FileWriter.get_project_files(project_dir)

        return {
            "project_id": project_id,
            "project_dir": str(project_dir),
            "metadata": metadata,
            "files": files,
            "file_count": len(files),
        }

    async def regenerate_file(
        self,
        project_id: str,
        filename: str,
        rules: Optional[GenerationRules] = None,
    ) -> Tuple[bool, str]:
        """
        Regenerate a specific file in a project.

        Args:
            project_id: Project ID
            filename: Name of file to regenerate
            rules: Optional generation rules

        Returns:
            Tuple of (success, message)
        """
        logger.info(f"Regenerating {filename} in project {project_id}")

        try:
            project_info = self.get_project_info(project_id)
            metadata = project_info["metadata"]
            original_prompt = metadata.get("original_prompt", "")

            if not original_prompt:
                return False, "Could not find original prompt in metadata"

            # Generate code again
            result = await self.generate_api(original_prompt, rules, project_id)

            if not result.success:
                return False, result.error_message or "Generation failed"

            # Update the specific file
            project_dir = settings.GENERATED_PROJECTS_DIR / project_id
            if filename in result.code_blocks:
                file_content = result.code_blocks[filename].content
                FileWriter.write_file(project_dir, filename, file_content)
                return True, f"Successfully regenerated {filename}"
            else:
                return False, f"File {filename} not found in generated blocks"

        except Exception as e:
            logger.error(f"Failed to regenerate file: {str(e)}")
            return False, str(e)

