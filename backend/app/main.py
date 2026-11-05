import logging
import re
import time
import uuid
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from collections import Counter

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.api.v1.router import api_router
from app.core.config import settings
from app.database.session import engine


class RequestLogDefaultsFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        for field in ("request_id", "correlation_id", "method", "path", "status_code"):
            if not hasattr(record, field):
                setattr(record, field, "-")
        return True


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s %(levelname)s %(name)s %(message)s "
        "request_id=%(request_id)s correlation_id=%(correlation_id)s "
        "method=%(method)s path=%(path)s status_code=%(status_code)s"
    ),
)
for handler in logging.getLogger().handlers:
    handler.addFilter(RequestLogDefaultsFilter())

logger = logging.getLogger("forgeform.api")
started_at = time.monotonic()
request_counts: dict[str, deque[float]] = defaultdict(deque)
http_requests: Counter[tuple[str, str, int]] = Counter()
http_duration: defaultdict[tuple[str, str, int], float] = defaultdict(float)


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await engine.dispose()


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_started = time.perf_counter()
        request_id = request.headers.get("X-Request-ID", "")[:100] or str(uuid.uuid4())
        correlation_id = request.headers.get("X-Correlation-ID", "")[:100]
        if not re.fullmatch(r"[A-Za-z0-9._:-]{1,100}", correlation_id):
            correlation_id = str(uuid.uuid4())

        is_login = request.url.path.endswith("/auth/login")
        is_public_form = request.url.path == "/api/v1/contact" or request.url.path.startswith("/api/v1/bookings")
        is_marketing_event = request.method == "POST" and request.url.path == "/api/v1/marketing-events"
        if is_login or is_public_form or is_marketing_event:
            limit = 5 if is_login else 10 if is_public_form else 120
            client = request.client.host if request.client else "unknown"
            rate_scope = "login" if is_login else "public-form" if is_public_form else "analytics"
            bucket = request_counts[client + rate_scope]
            now = time.monotonic()
            while bucket and now - bucket[0] > 60:
                bucket.popleft()
            if len(bucket) >= limit:
                return JSONResponse(
                    status_code=429,
                    headers={"Retry-After": "60", "X-Request-ID": request_id},
                    content={"success": False, "message": "Too many requests. Please try again later.", "errors": {}, "meta": None},
                )
            bucket.append(now)

        request.state.request_id = request_id
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        route = request.scope.get("route")
        route_path = getattr(route, "path", None) or "unmatched"
        metric_key = (request.method, route_path, response.status_code)
        http_requests[metric_key] += 1
        http_duration[metric_key] += time.perf_counter() - request_started
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        logger.info("http_request", extra={
            "request_id": request_id,
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
        })
        return response


class RequestSizeLimitMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        content_length = headers.get(b"content-length")
        if content_length:
            try:
                if int(content_length) > settings.max_request_bytes:
                    await self._reject(send, 413, "Request body is too large")
                    return
            except ValueError:
                await self._reject(send, 400, "Invalid content length")
                return

        messages: list[Message] = []
        body_size = 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            body_size += len(message.get("body", b""))
            if body_size > settings.max_request_bytes:
                await self._reject(send, 413, "Request body is too large")
                return
            messages.append(message)
            if not message.get("more_body", False):
                break

        index = 0

        async def replay_receive() -> Message:
            nonlocal index
            if index < len(messages):
                message = messages[index]
                index += 1
                return message
            return await receive()

        await self.app(scope, replay_receive, send)

    @staticmethod
    async def _reject(send: Send, code: int, message: str) -> None:
        body = (
            '{"success":false,"message":"'
            + message
            + '","errors":{},"meta":null}'
        ).encode("utf-8")
        await send({
            "type": "http.response.start",
            "status": code,
            "headers": [(b"content-type", b"application/json"), (b"content-length", str(len(body)).encode("ascii"))],
        })
        await send({"type": "http.response.body", "body": body})


app = FastAPI(
    title=settings.app_name,
    description="Forge & Form Personal Training API",
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan,
)
app.add_middleware(RequestContextMiddleware)
app.add_middleware(RequestSizeLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Idempotency-Key", "X-Correlation-ID", "X-Request-ID"],
)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors: dict[str, list[str]] = {}
    for error in exc.errors():
        field = ".".join(str(item) for item in error["loc"] if item != "body") or "request"
        errors.setdefault(field, []).append(error["msg"])
    return JSONResponse(status_code=422, content={
        "success": False,
        "message": "Validation failed",
        "errors": errors,
        "meta": None,
    })


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException):
    message = exc.detail if isinstance(exc.detail, str) else "Request could not be completed"
    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content={"success": False, "message": message, "errors": {}, "meta": None},
    )


@app.exception_handler(SQLAlchemyError)
async def database_error_handler(request: Request, exc: SQLAlchemyError):
    logger.error(
        "database_operation_failed",
        extra={"request_id": getattr(request.state, "request_id", None), "error_type": type(exc).__name__},
    )
    return JSONResponse(status_code=503, content={
        "success": False, "message": "The service is temporarily unavailable", "errors": {}, "meta": None,
    })


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.info(
        "database_constraint_conflict",
        extra={"request_id": getattr(request.state, "request_id", None)},
    )
    return JSONResponse(status_code=409, content={
        "success": False, "message": "The requested record conflicts with existing data", "errors": {}, "meta": None,
    })


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    logger.error(
        "unhandled_application_error",
        extra={"request_id": getattr(request.state, "request_id", None), "error_type": type(exc).__name__},
    )
    return JSONResponse(status_code=500, content={
        "success": False, "message": "An unexpected error occurred", "errors": {}, "meta": None,
    })


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/ready")
async def ready():
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))
    return {"status": "ready"}


@app.get(f"{settings.api_v1_prefix}/health/database")
async def database_health():
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        logger.error("database_health_failed", extra={"error_type": type(exc).__name__})
        return JSONResponse(status_code=503, content={"status": "unavailable"})
    return {"status": "ok"}


@app.get(f"{settings.api_v1_prefix}/health/kafka")
async def kafka_health():
    return {"status": "not_configured" if not settings.kafka_bootstrap_servers else "managed_by_outbox_worker"}


@app.get("/metrics")
async def metrics():
    uptime = max(0, int(time.monotonic() - started_at))
    lines = [
        "# HELP forgeform_uptime_seconds Process uptime in seconds.",
        "# TYPE forgeform_uptime_seconds gauge",
        f"forgeform_uptime_seconds {uptime}",
        "# HELP forgeform_http_requests_total Completed HTTP requests.",
        "# TYPE forgeform_http_requests_total counter",
        "# HELP forgeform_http_request_duration_seconds_sum Sum of request duration.",
        "# TYPE forgeform_http_request_duration_seconds_sum counter",
        "# HELP forgeform_http_request_duration_seconds_count Number of timed requests.",
        "# TYPE forgeform_http_request_duration_seconds_count counter",
    ]
    for (method, route, code), count in http_requests.items():
        labels = f'method="{method}",route="{route}",status="{code}"'
        lines.append(f"forgeform_http_requests_total{{{labels}}} {count}")
        lines.append(f"forgeform_http_request_duration_seconds_sum{{{labels}}} {http_duration[(method, route, code)]:.6f}")
        lines.append(f"forgeform_http_request_duration_seconds_count{{{labels}}} {count}")
    return Response(
        content="\n".join(lines) + "\n",
        media_type="text/plain; version=0.0.4",
        headers={"Cache-Control": "no-store"},
    )
