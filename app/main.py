import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.database import Base, engine
from app.metrics import PrometheusMiddleware, metrics_response
from app.routes.pages import router as pages_router
from app.routes.tasks import router as tasks_router

logger = logging.getLogger("taskflow")


def wait_for_database(attempts: int = 30, delay_seconds: float = 1.0) -> None:
    last_error: Exception | None = None
    for _ in range(attempts):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return
        except Exception as exc:  # noqa: BLE001 - retry until the database is ready
            last_error = exc
            time.sleep(delay_seconds)
    raise RuntimeError("Could not connect to the database") from last_error


@asynccontextmanager
async def lifespan(_app: FastAPI):
    wait_for_database()
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="TaskFlow",
    description="Todo management application for a DevOps demonstration project.",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(PrometheusMiddleware)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(tasks_router)
app.include_router(pages_router)


@app.get("/health")
def health() -> JSONResponse:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001 - health must not raise 500
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "detail": str(exc),
            },
        )
    return JSONResponse(
        status_code=200,
        content={"status": "healthy", "database": "connected"},
    )


@app.get("/metrics")
def metrics():
    return metrics_response()


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    _request: Request, exc: Exception
) -> JSONResponse:
    logger.exception("Unhandled application error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
