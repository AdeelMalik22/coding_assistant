"""Ollama LLM integration module."""

import httpx
import asyncio
import json
from typing import Optional, AsyncGenerator
from utils.logger import get_logger
from utils.errors import OllamaException, PromptValidationException
from config.settings import settings

logger = get_logger(__name__)


class OllamaClient:
    """Async client for Ollama API integration."""

    def __init__(
        self,
        base_url: str = settings.OLLAMA_BASE_URL,
        model: str = settings.OLLAMA_MODEL,
        timeout: int = settings.OLLAMA_TIMEOUT,
    ):
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
        self._client = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    async def health_check(self) -> bool:
        """Check if Ollama service is available."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama health check failed: {str(e)}")
            return False

    async def generate(self, prompt: str, model: Optional[str] = None) -> str:
        """
        Generate code using Ollama API.

        Args:
            prompt: The prompt to send to the LLM
            model: Optional model override

        Returns:
            Generated text response

        Raises:
            OllamaException: If generation fails
            PromptValidationException: If prompt is invalid
        """
        if not prompt or len(prompt) == 0:
            raise PromptValidationException("Prompt cannot be empty")

        if len(prompt) > settings.MAX_PROMPT_SIZE:
            raise PromptValidationException(
                f"Prompt exceeds maximum size of {settings.MAX_PROMPT_SIZE} characters"
            )

        model = model or self.model

        try:
            response_text = ""
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Sending request to Ollama at {self.base_url}...")
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "temperature": 0.2,
                    },
                ) as response:
                    logger.info(f"Got response status: {response.status_code}")
                    if response.status_code != 200:
                        error_text = ""
                        async for chunk in response.aiter_text():
                            error_text += chunk
                        logger.error(f"Ollama error: {error_text}")
                        raise OllamaException(
                            f"Ollama API error: {response.status_code}"
                        )

                    async for line in response.aiter_text():
                        response_text += line

            logger.info(f"Got response: {response_text[:100]}...")

            # Parse JSON response and extract just the text content
            try:
                response_data = json.loads(response_text)
                # Ollama returns: {"model": "...", "response": "actual text here", ...}
                extracted_text = response_data.get("response", "").strip()
                if extracted_text:
                    logger.info(f"Successfully generated text ({len(extracted_text)} chars)")
                    return extracted_text
                else:
                    logger.warning("Response field empty, returning full response")
                    return response_text
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {str(e)}, response: {response_text[:200]}")
                # If not valid JSON, return as-is
                return response_text.strip()

        except httpx.ConnectError as e:
            logger.error(f"Connection error: {str(e)}")
            raise OllamaException(
                f"Failed to connect to Ollama at {self.base_url}. "
                f"Make sure Ollama is running: ollama serve"
            )
        except asyncio.TimeoutError:
            raise OllamaException(f"Ollama request timed out after {self.timeout}s")
        except Exception as e:
            logger.error(f"Ollama generation error: {str(e)}")
            raise OllamaException(f"Failed to generate code: {str(e)}")

    async def generate_stream(self, prompt: str, model: Optional[str] = None) -> AsyncGenerator[str, None]:
        """
        Generate code using Ollama API with streaming response.

        Args:
            prompt: The prompt to send to the LLM
            model: Optional model override

        Yields:
            Chunks of generated text

        Raises:
            OllamaException: If generation fails
            PromptValidationException: If prompt is invalid
        """
        if not prompt or len(prompt) == 0:
            raise PromptValidationException("Prompt cannot be empty")

        if len(prompt) > settings.MAX_PROMPT_SIZE:
            raise PromptValidationException(
                f"Prompt exceeds maximum size of {settings.MAX_PROMPT_SIZE} characters"
            )

        model = model or self.model

        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": True,
                        "temperature": 0.2,
                    },
                    timeout=self.timeout,
                ) as response:
                    if response.status_code != 200:
                        raise OllamaException(
                            f"Ollama API error: {response.status_code}"
                        )

                    async for line in response.aiter_text():
                        if line.strip():
                            yield line

        except httpx.ConnectError:
            raise OllamaException(
                f"Failed to connect to Ollama at {self.base_url}"
            )
        except asyncio.TimeoutError:
            raise OllamaException(f"Ollama request timed out after {self.timeout}s")
        except Exception as e:
            logger.error(f"Ollama streaming error: {str(e)}")
            raise OllamaException(f"Failed to generate code: {str(e)}")

    async def list_models(self) -> list:
        """List available models on Ollama."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags")
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            logger.error(f"Failed to list models: {str(e)}")
            return []


# Singleton instance
_ollama_client = None


async def get_ollama_client() -> OllamaClient:
    """Get or create an Ollama client instance."""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client

