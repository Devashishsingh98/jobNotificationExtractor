"""Government Job Notification System — FastAPI Backend."""

import time
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.routes import auth, users, notifications, admin
from app.logging_config import logger, log_api_call, log_exception

app = FastAPI(
    title="Job Notification System",
    description="Automated government job notification system with eligibility matching",
    version="1.0.0",
)

# CORS — allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all API requests with timing."""
    start_time = time.time()

    try:
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000
        log_api_call(request.method, request.url.path, response.status_code, duration_ms)
        return response
    except Exception as exc:
        duration_ms = (time.time() - start_time) * 1000
        log_exception(exc, f"{request.method} {request.url.path}")
        log_api_call(request.method, request.url.path, 500, duration_ms)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )


# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    logger.warning(f"Validation error on {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions."""
    log_exception(exc, f"Unhandled exception on {request.method} {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred"}
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Log app startup."""
    logger.info("🚀 Job Notification System starting up...")
    logger.info(f"📍 Environment: {app.version}")


@app.on_event("shutdown")
async def shutdown_event():
    """Log app shutdown."""
    logger.info("🛑 Job Notification System shutting down...")


# Register routes
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(notifications.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    return {
        "name": "Job Notification System",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
