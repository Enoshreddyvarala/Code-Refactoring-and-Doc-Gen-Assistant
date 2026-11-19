"""Gemini AI Service Module for CodeMate AI.

Manages interactions with Google Gemini models using the modern Google GenAI SDK
with fallback support. Features robust error handling, secure key management,
and configurable model selection.
"""

import os
from typing import Optional, Tuple
from dotenv import load_dotenv

# Load local environment variables from .env if present
load_dotenv(override=True)

# Default model recommendation (fast, reliable, free-tier friendly)
DEFAULT_GEMINI_MODEL = "gemini-3.5-flash-lite"
SUPPORTED_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.8-flash",
    "gemini-3.8-pro",
    "gemini-3.5-flash",
    "gemini-3.5-pro",
]
FALLBACK_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
]


class GeminiKeyMissingError(Exception):
    """Raised when no Gemini API key is configured."""
    pass


class GeminiAPIError(Exception):
    """Raised when the Gemini API encounters an error during generation."""
    pass


class GeminiService:
    """Service wrapper for Google Gemini GenAI interactions."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """Initialize the service.

        Args:
            api_key: Optional API key. If omitted, loaded from GEMINI_API_KEY env var.
            model_name: Optional model identifier. Defaults to GEMINI_MODEL env var or gemini-2.5-flash.
        """
        self._api_key = api_key
        self._model_name = model_name

    def get_api_key(self, override_key: Optional[str] = None) -> Optional[str]:
        """Resolve the active API key with precedence: override -> instance -> environment."""
        if override_key and override_key.strip():
            return override_key.strip()
        if self._api_key and self._api_key.strip():
            return self._api_key.strip()
        return os.getenv("GEMINI_API_KEY", "").strip() or None

    def is_configured(self, override_key: Optional[str] = None) -> bool:
        """Check whether a non-empty API key is available."""
        key = self.get_api_key(override_key)
        return bool(key and len(key) > 5)

    def get_model_name(self, override_model: Optional[str] = None) -> str:
        """Resolve the active Gemini model name."""
        if override_model and override_model.strip():
            return override_model.strip()
        if self._model_name and self._model_name.strip():
            return self._model_name.strip()
        return os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip() or DEFAULT_GEMINI_MODEL

    def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        override_key: Optional[str] = None,
        override_model: Optional[str] = None,
    ) -> str:
        """Send a generation request to the Gemini model.

        Args:
            prompt: User prompt content.
            system_instruction: Optional system instruction / persona guiding generation.
            override_key: Optional one-off API key override.
            override_model: Optional one-off model override.

        Returns:
            The generated text string.

        Raises:
            GeminiKeyMissingError: If no API key is set.
            GeminiAPIError: If the API call fails or model returns an empty response.
        """
        key = self.get_api_key(override_key)
        if not key:
            raise GeminiKeyMissingError(
                "Gemini API key is not configured. Please set GEMINI_API_KEY in your .env file "
                "or provide it in the CodeMate AI sidebar settings."
            )

        model = self.get_model_name(override_model)

        # Models to attempt: primary model first, then fallback models if quota is exhausted
        models_to_try = [model]
        for fb in FALLBACK_MODELS:
            if fb != model and fb not in models_to_try:
                models_to_try.append(fb)

        last_error = None
        for current_model in models_to_try:
            try:
                from google import genai
                client = genai.Client(api_key=key)

                config = {}
                if system_instruction:
                    config["system_instruction"] = system_instruction

                response = client.models.generate_content(
                    model=current_model,
                    contents=prompt,
                    config=config if config else None,
                )

                if response and hasattr(response, "text") and response.text:
                    return response.text.strip()
                raise GeminiAPIError("The Gemini model returned an empty response.")

            except Exception as exc:
                err_str = str(exc)
                last_error = exc
                # If quota exhausted (429), try next model in fallback list
                if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str:
                    continue
                # If key invalid or bad request, don't retry
                if "API_KEY_INVALID" in err_str or "INVALID_ARGUMENT" in err_str:
                    raise GeminiAPIError("The provided Gemini API key appears invalid. Please verify your key at Google AI Studio.") from exc
                raise GeminiAPIError(f"Gemini API request failed: {err_str}") from exc

        # If all models in fallback chain were exhausted
        error_msg = str(last_error) if last_error else ""
        if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
            raise GeminiAPIError("Gemini API daily quota exceeded across all available models. Please wait or use a paid/different API key.") from last_error
        raise GeminiAPIError(f"Gemini API request failed: {error_msg}") from last_error


# Global singleton instance for easy import across services
gemini_service = GeminiService()
