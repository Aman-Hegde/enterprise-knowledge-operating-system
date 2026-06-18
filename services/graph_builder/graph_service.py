"""Store extracted entities and relationships in Neo4j."""

import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from neo4j import GraphDatabase

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def _neo4j_settings() -> tuple[str, str, str, str]:
    """Read and validate the Neo4j connection settings."""
    names = (
        "NEO4J_URI",
        "NEO4J_USERNAME",
        "NEO4J_PASSWORD",
        "NEO4J_DATABASE",
    )
    values = tuple(os.getenv(name, "").strip() for name in names)
    missing = [name for name, value in zip(names, values) if not value]

    if missing:
        raise ValueError(f"Missing Neo4j settings in .env: {', '.join(missing)}")

    return values


@lru_cache(maxsize=1)
def _get_driver():
    """Create one reusable Neo4j driver for the current process."""
    uri, username, password, _ = _neo4j_settings()
    return GraphDatabase.driver(uri, auth=(username, password))


def _relationship_type(relation: str) -> str:
    """Convert a relationship name into a safe Cypher identifier."""
    safe_relation = re.sub(r"[^A-Za-z0-9_]+", "_", relation.strip()).upper()
    safe_relation = safe_relation.strip("_")

    if not safe_relation or not safe_relation[0].isalpha():
        raise ValueError(f"Invalid relationship type: {relation!r}")

    return safe_relation


def _entity_label(entity_type: str) -> str:
    """Convert an entity type into a safe Neo4j node label."""
    safe_label = re.sub(r"[^A-Za-z0-9_]+", "_", entity_type.strip())
    safe_label = safe_label.strip("_")

    if not safe_label or not safe_label[0].isalpha():
        raise ValueError(f"Invalid entity type: {entity_type!r}")

    return safe_label


def create_entity(name: str, type: str) -> int:
    """Merge one entity and return 1 only when Neo4j creates a new node."""
    if not name.strip() or not type.strip():
        raise ValueError("Entity name and type cannot be empty")

    _, _, _, database = _neo4j_settings()
    entity_label = _entity_label(type)
    query = f"""
    MERGE (entity:Entity:{entity_label} {{name: $name}})
    ON CREATE SET entity.type = $type
    ON MATCH SET entity.type = $type
    """

    with _get_driver().session(database=database) as session:
        summary = session.run(query, name=name.strip(), type=type.strip()).consume()

    return summary.counters.nodes_created


def create_relationship(source: str, relation: str, target: str) -> int:
    """Merge one directed relationship and return its creation count."""
    if not source.strip() or not target.strip():
        raise ValueError("Relationship source and target cannot be empty")

    relation_type = _relationship_type(relation)
    _, _, _, database = _neo4j_settings()

    # The relationship type cannot be a query parameter, so it is strictly
    # sanitized before being inserted into the Cypher statement.
    query = f"""
    MERGE (source:Entity {{name: $source}})
    MERGE (target:Entity {{name: $target}})
    MERGE (source)-[relationship:{relation_type}]->(target)
    """

    with _get_driver().session(database=database) as session:
        summary = session.run(
            query,
            source=source.strip(),
            target=target.strip(),
        ).consume()

    return summary.counters.relationships_created


def build_graph(graph_data: dict[str, Any]) -> dict[str, int]:
    """Merge all extracted graph data and return Neo4j creation totals."""
    entities_created = 0
    relationships_created = 0

    for entity in graph_data.get("entities", []):
        entities_created += create_entity(entity["name"], entity["type"])

    for relationship in graph_data.get("relationships", []):
        relationships_created += create_relationship(
            relationship["source"],
            relationship["relation"],
            relationship["target"],
        )

    return {
        "entities_created": entities_created,
        "relationships_created": relationships_created,
    }
