# ./src/meal_planner/api/middleware.py

from __future__ import annotations

import logging
from typing import Any

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Standardize HTTPException responses."""
    logger.debug("HTTPException handled: %s %s", exc.status_code, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "http",
                "message": exc.detail,
            }
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Return a consistent error payload for validation failures."""
    logger.debug("Validation error: %s", exc.errors())
    # Sanitize errors: Pydantic v2 ctx may contain non-serializable objects
    sanitized = []
    for err in exc.errors():
        clean = {k: v for k, v in err.items() if k != "ctx"}
        if "ctx" in err and isinstance(err["ctx"], dict):
            clean["ctx"] = {k: str(v) for k, v in err["ctx"].items()}
        sanitized.append(clean)
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "type": "validation",
                "message": "Request validation failed",
                "details": sanitized,
            }
        },
    )


def register_api_middleware(app: Any) -> None:
    """Register middleware and exception handlers on the FastAPI app."""

    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
