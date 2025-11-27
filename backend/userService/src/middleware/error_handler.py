from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
import traceback
from src.core.logger import get_logger, generate_correlation_id, correlation_id

logger = get_logger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        corr_id = generate_correlation_id()
        token = correlation_id.set(corr_id)

        try:
            response = await call_next(request)
            return response
        except RequestValidationError as exc:
            logger.warning(f"Validation error: {exc}")
            return JSONResponse(
                status_code=422,
                content={"detail": "Validation error", "correlation_id": corr_id}
            )
        except Exception as exc:
            logger.error(f"Unhandled exception: {exc}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error", "correlation_id": corr_id}
            )
        finally:
            correlation_id.reset(token)


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        corr_id = request.headers.get("X-Correlation-ID", generate_correlation_id())
        token = correlation_id.set(corr_id)

        try:
            response = await call_next(request)
            response.headers["X-Correlation-ID"] = corr_id
            return response
        finally:
            correlation_id.reset(token)
