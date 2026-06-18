"""Small Gemini client used by the EKOS retrieval pipeline."""

import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

# Load configuration from the repository's .env file without logging secrets.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def generate_answer(prompt: str) -> str:
    """Send a prompt to Gemini and return its text response."""
    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured in .env")

    if not model_name:
        raise ValueError("GEMINI_MODEL is not configured in .env")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response")

    return response.text.strip()
