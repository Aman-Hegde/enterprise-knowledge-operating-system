"""Extract knowledge graph data from text with Gemini."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


class Entity(BaseModel):
    """A named item found in the source document."""

    name: str
    type: str


class Relationship(BaseModel):
    """A directed connection between two extracted entities."""

    source: str
    target: str
    relation: str


class GraphExtraction(BaseModel):
    """Structured knowledge graph output expected from Gemini."""

    entities: list[Entity]
    relationships: list[Relationship]


def extract_entities_and_relationships(text: str) -> dict[str, list[dict[str, str]]]:
    """Extract entities and relationships as validated JSON-compatible data."""
    if not text.strip():
        return {"entities": [], "relationships": []}

    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured in .env")

    if not model_name:
        raise ValueError("GEMINI_MODEL is not configured in .env")

    prompt = f"""Extract a knowledge graph from the document below.

Rules:
- Use only facts explicitly stated in the document.
- Give every entity a concise canonical name and type.
- Every relationship source and target must match an entity name exactly.
- Use uppercase snake case for relationship names, such as HAS_SKILL.
- Do not infer unsupported facts.
- Return only JSON matching the required schema.

Document:
{text}
"""

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json",
            response_schema=GraphExtraction,
        ),
    )

    # Structured output is preferred; parsing text is a defensive fallback.
    if response.parsed:
        graph_data = GraphExtraction.model_validate(response.parsed)
    elif response.text:
        graph_data = GraphExtraction.model_validate(json.loads(response.text))
    else:
        raise RuntimeError("Gemini returned an empty graph extraction response")

    return graph_data.model_dump()
