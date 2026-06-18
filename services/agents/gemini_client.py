"""Small Gemini client used by the EKOS retrieval pipeline."""

import os
from pathlib import Path
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors
import httpx
import requests

# Load configuration from the repository's .env file without logging secrets.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 2
FALLBACK_MESSAGE = (
    "I am unable to generate an answer right now. Please try again shortly."
)


def _is_temporary_api_error(error: errors.APIError) -> bool:
    """Return True for API status codes that are usually safe to retry."""
    return isinstance(error.code, int) and (
        error.code in {408, 429} or 500 <= error.code < 600
    )


def generate_answer(prompt: str) -> str:
    """Send a prompt to Gemini with retries for temporary failures."""
    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL")

    if not api_key:
        return FALLBACK_MESSAGE

    if not model_name:
        return FALLBACK_MESSAGE

    try:
        client = genai.Client(api_key=api_key)
    except Exception:
        # Client setup can fail before an API request is made.
        return FALLBACK_MESSAGE

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )

            if not response.text:
                raise RuntimeError("Gemini returned an empty response")

            return response.text.strip()
        except errors.APIError as error:
            # Invalid credentials and other permanent 4xx errors should not retry.
            if not _is_temporary_api_error(error):
                return FALLBACK_MESSAGE
        except (
            httpx.TimeoutException,
            httpx.TransportError,
            requests.RequestException,
            errors.UnknownApiResponseError,
            RuntimeError,
        ):
            # Timeouts, connection failures, and empty responses may be temporary.
            pass

        if attempt < MAX_ATTEMPTS:
            time.sleep(RETRY_DELAY_SECONDS)

    return FALLBACK_MESSAGE
