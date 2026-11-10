"""Idempotency middleware for mutating requests."""
from __future__ import annotations

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class IdempotencyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, ttl_seconds: int = 300):
        super().__init__(app)
        self.ttl = ttl_seconds
        self.cache: dict[str, tuple[float, int, dict[str, str], bytes]] = {}

    async def dispatch(self, request: Request, call_next):
        if request.method not in ("POST", "PUT", "PATCH"):
            return await call_next(request)
        key = request.headers.get("Idempotency-Key")
        if not key:
            return await call_next(request)
        # include method+path in cache key to avoid cross-endpoint collisions
        cache_key = f"{request.method}:{request.url.path}:{key}"
        now = time.time()
        # evict expired
        expired = [k for k, v in self.cache.items() if now - v[0] > self.ttl]
        for k in expired:
            del self.cache[k]
        if cache_key in self.cache:
            _, status, headers, body = self.cache[cache_key]
            resp = Response(content=body, status_code=status, media_type="application/json")
            for h, v in headers.items():
                if h.lower() not in ("content-length",):
                    resp.headers[h] = v
            resp.headers["Idempotent-Replayed"] = "true"
            return resp
        response = await call_next(request)
        # cache only successful-ish responses
        body = b""
        async for chunk in response.body_iterator:
            body += chunk
        if response.status_code < 500:
            self.cache[cache_key] = (now, response.status_code, dict(response.headers), body)
        new_resp = Response(content=body, status_code=response.status_code, media_type=response.media_type)
        for h, v in response.headers.items():
            if h.lower() not in ("content-length",):
                new_resp.headers[h] = v
        return new_resp
