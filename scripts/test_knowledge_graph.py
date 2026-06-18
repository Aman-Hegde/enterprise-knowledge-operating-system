"""Manual end-to-end test for the Sprint 5 knowledge graph builder."""

import json
from pathlib import Path
import sys

# Add the repository root so this script can be run directly.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from services.graph_builder.entity_extractor import (
    extract_entities_and_relationships,
)
from services.graph_builder.graph_service import build_graph
from services.ingestion.pdf_loader import extract_text_from_pdf


def main() -> None:
    """Extract graph data from the sample PDF and store it in Neo4j."""
    pdf_path = PROJECT_ROOT / "data" / "sample_documents" / "sample.pdf"
    text = extract_text_from_pdf(str(pdf_path))

    graph_data = extract_entities_and_relationships(text)

    print("=" * 60)
    print("EXTRACTED KNOWLEDGE GRAPH")
    print("=" * 60)
    print(json.dumps(graph_data, indent=2))

    totals = build_graph(graph_data)

    print("\n" + "=" * 60)
    print(f"Total entities created: {totals['entities_created']}")
    print(f"Total relationships created: {totals['relationships_created']}")


if __name__ == "__main__":
    main()
