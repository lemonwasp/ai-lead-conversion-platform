"""FastAPI entry point for the reconstruction."""

from fastapi import FastAPI

from lead_intelligence.schemas import HealthResponse

app = FastAPI(
    title="AI Lead Conversion Platform",
    summary="Privacy-safe lead scoring and outreach drafting",
    version="0.1.0",
)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    """Report whether the API process is ready to accept requests."""

    return HealthResponse(status="ok", version=app.version)
