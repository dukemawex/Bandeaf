from __future__ import annotations

import logging
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import settings
from app.routers import alerts, auth, health, responders, routes, stream, users, zones


class SafeLogFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        msg = str(record.getMessage())
        redacted = msg
        for token in ["phone", "password", "token", "emergency_contacts"]:
            redacted = redacted.replace(token, "[REDACTED]")
        record.msg = redacted
        return True


limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])

app = FastAPI(title=settings.APP_NAME, version="0.1.0", openapi_url=f"{settings.API_V1_PREFIX}/openapi.json")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

logging.getLogger("uvicorn.access").addFilter(SafeLogFilter())


@app.middleware("http")
async def request_audit_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    logging.getLogger("safenet.audit").info(
        "request path=%s method=%s status=%s duration_ms=%s",
        request.url.path,
        request.method,
        response.status_code,
        duration_ms,
    )
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, exc: Exception):
    logging.getLogger("safenet.error").exception("Unhandled exception: %s", exc.__class__.__name__)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(health.router, prefix=settings.API_V1_PREFIX)
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(alerts.router, prefix=settings.API_V1_PREFIX)
app.include_router(zones.router, prefix=settings.API_V1_PREFIX)
app.include_router(routes.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(responders.router, prefix=settings.API_V1_PREFIX)
app.include_router(stream.router, prefix=settings.API_V1_PREFIX)
