"""
Application middleware.

Provides:
- Request ID generation
- Request/response logging
- Request execution time
- Security headers
- Client/request metadata
"""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger


logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Request Logging Middleware
# ---------------------------------------------------------------------------

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs every HTTP request and response.

    It also adds:
        X-Request-ID
        X-Process-Time
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:

        # ---------------------------------------------------------------
        # Request ID
        # ---------------------------------------------------------------

        request_id = request.headers.get(
            "X-Request-ID"
        )

        if not request_id:
            request_id = str(uuid.uuid4())

        # Store request ID so it can be accessed by
        # endpoints/services through request.state.
        request.state.request_id = request_id

        # ---------------------------------------------------------------
        # Request Information
        # ---------------------------------------------------------------

        method = request.method
        path = request.url.path

        client_ip = (
            request.client.host
            if request.client
            else "unknown"
        )

        start_time = time.perf_counter()

        logger.info(
            "Request started | "
            "request_id=%s | "
            "method=%s | "
            "path=%s | "
            "client=%s",
            request_id,
            method,
            path,
            client_ip,
        )

        # ---------------------------------------------------------------
        # Execute Request
        # ---------------------------------------------------------------

        try:
            response = await call_next(request)

        except Exception:
            process_time = (
                time.perf_counter()
                - start_time
            )

            logger.exception(
                "Request failed | "
                "request_id=%s | "
                "method=%s | "
                "path=%s | "
                "duration=%.4fs",
                request_id,
                method,
                path,
                process_time,
            )

            raise

        # ---------------------------------------------------------------
        # Processing Time
        # ---------------------------------------------------------------

        process_time = (
            time.perf_counter()
            - start_time
        )

        process_time_ms = process_time * 1000

        # ---------------------------------------------------------------
        # Response Headers
        # ---------------------------------------------------------------

        response.headers[
            "X-Request-ID"
        ] = request_id

        response.headers[
            "X-Process-Time"
        ] = f"{process_time:.4f}"

        # ---------------------------------------------------------------
        # Response Logging
        # ---------------------------------------------------------------

        logger.info(
            "Request completed | "
            "request_id=%s | "
            "method=%s | "
            "path=%s | "
            "status=%s | "
            "duration=%.2fms",
            request_id,
            method,
            path,
            response.status_code,
            process_time_ms,
        )

        return response


# ---------------------------------------------------------------------------
# Security Headers Middleware
# ---------------------------------------------------------------------------

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds common HTTP security headers.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:

        response = await call_next(request)

        # Prevent MIME-type sniffing.
        response.headers[
            "X-Content-Type-Options"
        ] = "nosniff"

        # Prevent clickjacking.
        response.headers[
            "X-Frame-Options"
        ] = "DENY"

        # Control referrer information.
        response.headers[
            "Referrer-Policy"
        ] = "strict-origin-when-cross-origin"

        # Restrict browser features.
        response.headers[
            "Permissions-Policy"
        ] = (
            "camera=(), "
            "microphone=(self), "
            "geolocation=()"
        )

        # Basic Content Security Policy.
        response.headers[
            "Content-Security-Policy"
        ] = (
            "default-src 'self'; "
            "img-src 'self' data: https:; "
            "style-src 'self' 'unsafe-inline'; "
            "script-src 'self'; "
            "font-src 'self' data: https:; "
            "connect-src 'self' https:;"
        )

        return response


# ---------------------------------------------------------------------------
# Request Context Middleware
# ---------------------------------------------------------------------------

class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Stores useful request information in request.state.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:

        request.state.method = request.method

        request.state.path = request.url.path

        request.state.client_ip = (
            request.client.host
            if request.client
            else None
        )

        request.state.user_agent = (
            request.headers.get(
                "user-agent"
            )
        )

        return await call_next(request)


# ---------------------------------------------------------------------------
# Middleware Registration Helper
# ---------------------------------------------------------------------------

def register_middlewares(app) -> None:
    """
    Register all application middleware.

    Middleware order matters.

    Starlette executes middleware in reverse registration
    order around the request lifecycle.
    """

    app.add_middleware(
        SecurityHeadersMiddleware
    )

    app.add_middleware(
        RequestContextMiddleware
    )

    app.add_middleware(
        RequestLoggingMiddleware
    )
