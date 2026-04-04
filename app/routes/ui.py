"""UI routes using Jinja2 templates."""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import json

from utils.logger import get_logger
from app.ai.prompt_builder import GenerationRules
from services.generator_service import GeneratorService
from config.settings import settings

logger = get_logger(__name__)

router = APIRouter(tags=["ui"])

# Initialize generator service
generator = GeneratorService()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with prompt input form."""
    from jinja2 import Environment, FileSystemLoader

    env = Environment(loader=FileSystemLoader(settings.TEMPLATES_DIR))
    template = env.get_template("index.html")

    return template.render(
        title="AI-Powered API Builder",
        request=request,
    )


@router.post("/generate", response_class=HTMLResponse)
async def generate(request: Request):
    """
    Handle generation form submission.

    Args:
        request: FastAPI Request object

    Returns:
        HTML response with generation result or error
    """
    try:
        form_data = await request.form()

        prompt = form_data.get("prompt", "").strip()
        if not prompt:
            raise ValueError("Prompt cannot be empty")

        # Extract rules from form
        rules = GenerationRules(
            jwt_auth="jwt_auth" in form_data,
            crud_operations="crud_operations" in form_data,
            user_model="user_model" in form_data,
            database="database" in form_data,
        )

        logger.info(f"Processing generation request: {prompt[:100]}...")

        # Generate API
        result = await generator.generate_api(prompt, rules)

        if not result.success:
            from jinja2 import Environment, FileSystemLoader
            env = Environment(loader=FileSystemLoader(settings.TEMPLATES_DIR))
            template = env.get_template("error.html")

            return template.render(
                title="Generation Error",
                error_message=result.error_message or "Unknown error occurred",
                request=request,
            )

        # Redirect to results page
        return RedirectResponse(
            url=f"/results/{result.project_id}",
            status_code=303
        )

    except Exception as e:
        logger.error(f"Generation error: {str(e)}", exc_info=True)
        from jinja2 import Environment, FileSystemLoader
        env = Environment(loader=FileSystemLoader(settings.TEMPLATES_DIR))
        template = env.get_template("error.html")

        return template.render(
            title="Generation Error",
            error_message=str(e),
            request=request,
        )


@router.get("/results/{project_id}", response_class=HTMLResponse)
async def results(request: Request, project_id: str):
    """
    Display generated code results.

    Args:
        project_id: Project ID
        request: FastAPI Request object

    Returns:
        HTML response with generated code
    """
    try:
        info = generator.get_project_info(project_id)

        from jinja2 import Environment, FileSystemLoader
        env = Environment(loader=FileSystemLoader(settings.TEMPLATES_DIR))
        template = env.get_template("results.html")

        # Prepare files for display
        files_display = []
        for filename, content in info["files"].items():
            files_display.append({
                "name": filename,
                "content": content,
                "lines": len(content.split("\n")),
            })

        return template.render(
            title="Generation Results",
            project_id=project_id,
            files=files_display,
            metadata=info.get("metadata", {}),
            request=request,
        )

    except FileNotFoundError:
        from jinja2 import Environment, FileSystemLoader
        env = Environment(loader=FileSystemLoader(settings.TEMPLATES_DIR))
        template = env.get_template("error.html")

        return template.render(
            title="Project Not Found",
            error_message=f"Project {project_id} not found",
            request=request,
        )

    except Exception as e:
        logger.error(f"Error loading results: {str(e)}", exc_info=True)
        from jinja2 import Environment, FileSystemLoader
        env = Environment(loader=FileSystemLoader(settings.TEMPLATES_DIR))
        template = env.get_template("error.html")

        return template.render(
            title="Error",
            error_message=str(e),
            request=request,
        )


@router.get("/api-reference", response_class=HTMLResponse)
async def api_reference(request: Request):
    """API reference documentation page."""
    from jinja2 import Environment, FileSystemLoader

    env = Environment(loader=FileSystemLoader(settings.TEMPLATES_DIR))
    template = env.get_template("api_reference.html")

    return template.render(
        title="API Reference",
        request=request,
    )


@router.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    """About page."""
    from jinja2 import Environment, FileSystemLoader

    env = Environment(loader=FileSystemLoader(settings.TEMPLATES_DIR))
    template = env.get_template("about.html")

    return template.render(
        title="About",
        request=request,
    )

