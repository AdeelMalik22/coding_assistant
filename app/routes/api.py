"""API routes for code generation."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import json
from utils.logger import get_logger
from utils.logger import get_logger
import asyncio

from utils.logger import get_logger
from app.ai.prompt_builder import GenerationRules
from services.generator_service import GeneratorService

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["generation"])

# Initialize generator service
generator = GeneratorService()


# Request/Response Models
class GenerateRequest(BaseModel):
    """Request to generate API code."""
    prompt: str
    jwt_auth: bool = False
    crud_operations: bool = False
    user_model: bool = False
    database: bool = True
    custom_rules: Optional[list] = None


class GenerateResponse(BaseModel):
    """Response from code generation."""
    project_id: str
    success: bool
    message: str
    files: Optional[dict] = None
    validation_summary: Optional[dict] = None
    error_message: Optional[str] = None


class ProjectInfoResponse(BaseModel):
    """Information about a generated project."""
    project_id: str
    project_dir: str
    files: dict
    metadata: dict
    file_count: int


class FileEditRequest(BaseModel):
    """Request to edit a file in a project."""
    content: str


class FileEditResponse(BaseModel):
    """Response from file edit."""
    success: bool
    message: str
    filename: str


# Endpoints

@router.post("/generate", response_model=GenerateResponse)
async def generate_api(request: GenerateRequest):
    """
    Generate code from a prompt.

    Args:
        request: Generation request with prompt

    Returns:
        GenerateResponse with generated code
    """
    logger.info(f"Received generation request: {request.prompt[:100]}...")

    try:
        # Build generation rules
        rules = GenerationRules(
            jwt_auth=request.jwt_auth,
            crud_operations=request.crud_operations,
            user_model=request.user_model,
            database=request.database,
            custom_rules=request.custom_rules or [],
        )

        # Generate code with timeout
        try:
            result = await asyncio.wait_for(
                generator.generate_api(request.prompt, rules),
                timeout=120.0  # 2 minute timeout
            )
        except asyncio.TimeoutError:
            logger.error("Generation timed out after 120 seconds")
            return GenerateResponse(
                project_id="timeout",
                success=False,
                message="Generation timed out",
                error_message="Generation took too long. Check if Ollama is running: ollama serve",
            )

        if not result.success:
            logger.error(f"Generation failed: {result.error_message}")
            return GenerateResponse(
                project_id=result.project_id,
                success=False,
                message="Code generation failed",
                error_message=result.error_message,
            )

        # Prepare file response
        files = {}
        if result.code_blocks:
            for filename, block in result.code_blocks.items():
                files[filename] = block.content
        else:
            logger.error("No code blocks generated")
            return GenerateResponse(
                project_id=result.project_id,
                success=False,
                message="No code generated",
                error_message="No output from LLM",
            )

        return GenerateResponse(
            project_id=result.project_id,
            success=True,
            message="Code generated successfully",
            files=files,
            validation_summary=result.metadata.get("validation_summary"),
        )

    except Exception as e:
        logger.error(f"Generation error: {str(e)}", exc_info=True)
        return GenerateResponse(
            project_id="error",
            success=False,
            message="Generation failed",
            error_message=str(e),
        )


@router.get("/projects/{project_id}", response_model=ProjectInfoResponse)
async def get_project_info(project_id: str):
    """
    Get information about a generated project.

    Args:
        project_id: Project ID

    Returns:
        ProjectInfoResponse with project details
    """
    try:
        info = generator.get_project_info(project_id)
        return ProjectInfoResponse(**info)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")
    except Exception as e:
        logger.error(f"Error retrieving project info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/files/{filename}")
async def get_file(project_id: str, filename: str):
    """
    Get a specific file from a project.

    Args:
        project_id: Project ID
        filename: Filename to retrieve

    Returns:
        File content as JSON
    """
    try:
        info = generator.get_project_info(project_id)

        if filename not in info["files"]:
            raise HTTPException(status_code=404, detail="File not found")

        return {
            "project_id": project_id,
            "filename": filename,
            "content": info["files"][filename],
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")
    except Exception as e:
        logger.error(f"Error retrieving file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/projects/{project_id}/files/{filename}",
    response_model=FileEditResponse
)
async def edit_file(
    project_id: str,
    filename: str,
    request: FileEditRequest
):
    """
    Edit a file in a project.

    Args:
        project_id: Project ID
        filename: Filename to edit
        request: New file content

    Returns:
        FileEditResponse with success status
    """
    from pathlib import Path
    from config.settings import settings
    from utils.helpers import safe_write_file

    try:
        project_dir = settings.GENERATED_PROJECTS_DIR / project_id

        if not project_dir.exists():
            raise HTTPException(status_code=404, detail="Project not found")

        filepath = project_dir / filename

        # Security check: ensure file is within project directory
        if not str(filepath.resolve()).startswith(str(project_dir.resolve())):
            raise HTTPException(status_code=400, detail="Invalid file path")

        # Write file
        safe_write_file(filepath, request.content)

        return FileEditResponse(
            success=True,
            message=f"Successfully updated {filename}",
            filename=filename,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error editing file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/{project_id}/regenerate/{filename}")
async def regenerate_file(project_id: str, filename: str):
    """
    Regenerate a specific file in a project.

    Args:
        project_id: Project ID
        filename: Filename to regenerate

    Returns:
        Response with success status
    """
    try:
        success, message = await generator.regenerate_file(project_id, filename)

        if not success:
            raise HTTPException(status_code=400, detail=message)

        return {"success": True, "message": message}

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")
    except Exception as e:
        logger.error(f"Error regenerating file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "api-generator"}

