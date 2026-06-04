"""
main.py — versão de debug para capturar o erro 500.
Após identificar o erro, remova as linhas print/traceback.
"""

import logging
import traceback as tb

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.core.database import check_db_connection
from app.core.settings import settings
from app.routers import dashboard_router, log_router, order_router, product_router


# ─────────────────────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.DEBUG if settings.ENVIRONMENT == "development" else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Instância principal
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Logistics System API",
    description="Gerenciamento de produtos, pedidos e logs de auditoria.",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)


# ─────────────────────────────────────────────────────────────────────────────
# CORS
# ─────────────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────────────────────
# Exception handlers globais
# ─────────────────────────────────────────────────────────────────────────────

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status_code": exc.status_code,
            "error": _status_para_tipo(exc.status_code),
            "message": exc.detail,
        },
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status_code": 422,
            "error": "validation_error",
            "message": "Dados inválidos na requisição",
            "detail": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    import traceback
    erro_completo = traceback.format_exc()
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status_code": 500,
            "error": "internal_server_error",
            "message": str(exc),          # ← mostra o erro real
            "traceback": erro_completo,   # ← mostra o traceback completo
        },
    )


def _status_para_tipo(status_code: int) -> str:
    mapa = {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        409: "conflict",
        422: "validation_error",
        500: "internal_server_error",
    }
    return mapa.get(status_code, "error")


# ─────────────────────────────────────────────────────────────────────────────
# Eventos de ciclo de vida
# ─────────────────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def on_startup() -> None:
    logger.info("Iniciando aplicação [%s]...", settings.ENVIRONMENT)
    if not check_db_connection():
        logger.critical("Banco de dados inacessível. Abortando.")
        raise RuntimeError("Database unreachable on startup.")
    logger.info("Banco de dados OK.")
    logger.info("Aplicação pronta para receber requisições.")


# ─────────────────────────────────────────────────────────────────────────────
# Routers
# ─────────────────────────────────────────────────────────────────────────────

API_PREFIX = "/api/v1"

app.include_router(product_router,   prefix=API_PREFIX)
app.include_router(order_router,     prefix=API_PREFIX)
app.include_router(log_router,       prefix=API_PREFIX)
app.include_router(dashboard_router, prefix=API_PREFIX)


# ─────────────────────────────────────────────────────────────────────────────
# Health check
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["Infra"], summary="Status da aplicação e do banco")
def health_check() -> dict:
    db_ok = check_db_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "up" if db_ok else "down",
        "environment": settings.ENVIRONMENT,
    }