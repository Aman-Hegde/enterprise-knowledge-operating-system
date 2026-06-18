"""Read entity relationships from the EKOS Neo4j knowledge graph."""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from neo4j import GraphDatabase

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def _neo4j_settings() -> tuple[str, str, str, str]:
    """Load and validate Neo4j connection settings from .env."""
    variable_names = (
        "NEO4J_URI",
        "NEO4J_USERNAME",
        "NEO4J_PASSWORD",
        "NEO4J_DATABASE",
    )
    values = tuple(os.getenv(name, "").strip() for name in variable_names)
    missing = [
        name
        for name, value in zip(variable_names, values)
        if not value
    ]

    if missing:
        raise ValueError(f"Missing Neo4j settings in .env: {', '.join(missing)}")

    return values


@lru_cache(maxsize=1)
def _get_driver():
    """Create one reusable Neo4j driver for this process."""
    uri, username, password, _ = _neo4j_settings()
    return GraphDatabase.driver(uri, auth=(username, password))


def find_entity_by_name(entity_name: str) -> dict[str, Any] | None:
    """Find the best exact or partial entity-name match in Neo4j."""
    if not entity_name.strip():
        return None

    _, _, _, database = _neo4j_settings()
    query = """
    MATCH (entity:Entity)
    WHERE toLower(entity.name) = toLower($entity_name)
       OR toLower(entity.name) CONTAINS toLower($entity_name)
    RETURN entity.name AS name,
           entity.type AS type,
           labels(entity) AS labels
    ORDER BY
        CASE WHEN toLower(entity.name) = toLower($entity_name) THEN 0 ELSE 1 END,
        size(entity.name)
    LIMIT 1
    """

    with _get_driver().session(database=database) as session:
        record = session.run(query, entity_name=entity_name.strip()).single()

    return dict(record) if record else None


def get_neighbors(entity_name: str, max_depth: int = 1) -> list[dict[str, str]]:
    """Return unique relationships within a bounded depth of an entity."""
    if not 1 <= max_depth <= 5:
        raise ValueError("max_depth must be between 1 and 5")

    entity = find_entity_by_name(entity_name)
    if not entity:
        return []

    _, _, _, database = _neo4j_settings()

    # Cypher does not parameterize path depth, so the validated integer is
    # inserted directly while all user-provided values remain parameters.
    query = f"""
    MATCH path=(entity:Entity {{name: $entity_name}})-[*1..{max_depth}]-(neighbor)
    UNWIND relationships(path) AS relationship
    WITH DISTINCT startNode(relationship) AS source,
                  type(relationship) AS relation,
                  endNode(relationship) AS target
    RETURN source.name AS source,
           relation,
           target.name AS target
    ORDER BY source, relation, target
    """

    with _get_driver().session(database=database) as session:
        records = session.run(query, entity_name=entity["name"])
        return [dict(record) for record in records]


def get_graph_context(entity_name: str) -> str:
    """Format an entity's direct relationships as readable context."""
    relationships = get_neighbors(entity_name, max_depth=1)
    return "\n".join(
        f"{item['source']} {item['relation']} {item['target']}"
        for item in relationships
    )
