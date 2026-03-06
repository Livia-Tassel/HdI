"""FastAPI application factory and main app."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from hdi.api.routers import dimension1, dimension2, dimension3, metadata


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Health Data Insight API",
        description="API for global health data analysis and visualization",
        version="0.1.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(metadata.router, prefix="/api/v1")
    app.include_router(dimension1.router, prefix="/api/v1")
    app.include_router(dimension2.router, prefix="/api/v1")
    app.include_router(dimension3.router, prefix="/api/v1")

    @app.get("/api/v1/health")
    async def health_check():
        return {"status": "ok", "version": "0.1.0"}

    return app


app = create_app()
