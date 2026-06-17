from fastapi import FastAPI

app = FastAPI(
    title="Enterprise Knowledge Operating System",
    description="API service for the EKOS knowledge platform.",
    version="0.1.0",
)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Return a simple service health response."""
    return {"status": "ok", "service": "ekos-backend"}
