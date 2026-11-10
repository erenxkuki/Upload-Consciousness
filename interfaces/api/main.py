"""FastAPI application factory."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse

from core.settings import get_settings
from storage.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    limiter = Limiter(key_func=get_remote_address, default_limits=["300/minute"]) if settings.env != "test" else None

    app = FastAPI(
        title="Upload Consciousness - UCC",
        version="0.1.0",
        description="Experimental research platform for digital human continuity.",
        lifespan=lifespan,
    )
    if limiter is not None:
        app.state.limiter = limiter
        from slowapi.middleware import SlowAPIMiddleware

        app.add_middleware(SlowAPIMiddleware)

        @app.exception_handler(RateLimitExceeded)
        async def _rate_limit_handler(request: Request, exc: RateLimitExceeded):
            return JSONResponse(status_code=429, content={"detail": "rate limit exceeded"})

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from interfaces.api.middleware.idempotency import IdempotencyMiddleware

    app.add_middleware(IdempotencyMiddleware)

    from interfaces.api.routers import (
        auth,
        cognition,
        continuity,
        embodiment,
        emotion,
        health,
        identity,
        memory,
        personality,
        world,
    )

    app.include_router(health.router)
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(identity.router, prefix="/api/v1")
    app.include_router(memory.router, prefix="/api/v1")
    app.include_router(emotion.router, prefix="/api/v1")
    app.include_router(personality.router, prefix="/api/v1")
    app.include_router(cognition.router, prefix="/api/v1")
    app.include_router(continuity.router, prefix="/api/v1")
    app.include_router(embodiment.router, prefix="/api/v1")
    app.include_router(world.router, prefix="/api/v1")

    return app


app = create_app()
