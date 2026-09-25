from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.middleware.correlation import CorrelationIdMiddleware
from app.schemas.response import APIResponse

setup_logging()
logger = structlog.get_logger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# CORS Middleware
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Correlation ID and Request Logging Middleware
app.add_middleware(CorrelationIdMiddleware)

# Attach Centralized Exception Handlers (AppException, HTTPException, RequestValidationError, Exception)
register_exception_handlers(app)


@app.get("/health", tags=["Health"], response_model=APIResponse[dict])
async def health_check():
    return APIResponse.ok(data={"status": "ok"})


app.include_router(api_router, prefix=settings.API_V1_STR)
