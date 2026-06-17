# Enterprise Knowledge Operating System (EKOS)

EKOS is a production-oriented skeleton for an enterprise knowledge platform using FastAPI, Neo4j, Qdrant, LangGraph, and Ragas.

This repository currently contains architecture scaffolding only. Business logic, agent workflows, ingestion pipelines, retrieval logic, and evaluation suites will be added later.

## Stack

- FastAPI backend
- Future React frontend
- Neo4j graph database
- Qdrant vector database
- LangGraph agent orchestration
- Ragas evaluation
- Docker Compose for local development

## Project Structure

```text
enterprise-knowledge-operating-system/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── evaluation/
│   │   ├── ingestion/
│   │   ├── models/
│   │   ├── retrieval/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   └── tests/
├── data/
├── docker/
├── docs/
├── frontend/
├── scripts/
├── services/
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Getting Started

Create a local environment file:

```bash
cp .env.example .env
```

Install backend dependencies:

```bash
pip install -r requirements.txt
```

Run the backend locally:

```bash
uvicorn backend.app.main:app --reload
```

Open the health endpoint:

```text
http://localhost:8000/health
```

## Docker

Docker support is scaffolded with services for the backend, Neo4j, Qdrant, and a future frontend.

```bash
docker compose up
```

Before using Docker, create `.env` from `.env.example` and replace placeholder values with local development values.

## Notes

- Do not commit real secrets.
- Keep implementation code inside `backend/app`.
- Keep infrastructure helpers inside `docker` and `scripts`.
- Keep design and architecture notes inside `docs`.
