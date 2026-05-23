"""Main Service"""

import os
import tracemalloc

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from loguru import logger

from api.v1.routers.report import report_router
from core.config import AppConfig

config = AppConfig()

tracemalloc.start()
if not os.path.exists(f"{config.BASE_DIR}/logs/"):
    os.makedirs(f"{config.BASE_DIR}/logs/")

LOG_LEVEL = "DEBUG" if config.DEBUG else "INFO"
logger.remove()
logger.add(
    f"{config.BASE_DIR}/logs/{{time:YYYY-MM-DD}}.log",
    rotation="00:00",
    retention="30 days",
    level=LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    backtrace=True,
    diagnose=True,
)

appAPI = FastAPI(
    version="1.0.0",
)


appAPI.add_middleware(
    CORSMiddleware,
    allow_origins=config.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

appAPI.include_router(report_router, prefix="/api/v1")


@appAPI.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.exception(f"Erro inesperado no servidor: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno ao processar a requisição."},
    )


@appAPI.get("/", tags=["Service"])
def root():
    """Redirect to docs"""
    return RedirectResponse(url="/docs")
