"""FastAPI entrypoint for the Essential Eight + FAIR Cyber Risk Quantification Engine."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import e8, fair, reports, scenario
from backend.config import AppSettings, get_settings


def create_app(settings: AppSettings | None = None) -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured application instance with routers and middleware attached.
    """

    settings = settings or get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level, logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    app = FastAPI(
        title="Essential Eight + FAIR Quantification Engine",
        description=(
            "Cyber risk analytics platform combining ACSC Essential Eight maturity "
            "assessment with FAIR-based quantitative modelling."
        ),
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.state.settings = settings

    app.include_router(e8.router, prefix="/e8", tags=["Essential Eight"])
    app.include_router(fair.router, prefix="/fair", tags=["FAIR"])
    app.include_router(scenario.router, prefix="/scenario", tags=["Scenarios"])
    app.include_router(reports.router, prefix="/report", tags=["Reporting"])

    @app.get("/health")
    def health() -> dict[str, str]:
        """Simple healthcheck endpoint."""

        return {"status": "ok"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=False)
