"""
main.py — ponto de entrada da aplicação.

Responsabilidades:
  - Configurar logging por ambiente
  - Criar a instância do FastAPI com metadados
  - Configurar CORS
  - Registrar exception handlers globais com resposta padronizada
  - Verificar conexão com banco no startup — aborta se inacessível
  - Registrar todos os routers com prefixo /api/v1
  - Expor /health com status real do banco para Docker e load balancer
"""

import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.core.database import check_db_connection
from app.core.settings import settings
from app.routers import dashboard_router, log_router, order_router, product_router


# ─────────────────────────────────────────────────────────────────────────────
# Logging — DEBUG em dev, INFO em produção
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
    # Swagger e ReDoc desabilitados em produção — não exponho contratos publicamente
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)


# ─────────────────────────────────────────────────────────────────────────────
# CORS — permite o frontend React acessar a API em desenvolvimento
# ─────────────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # porta padrão do Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────────────────────
# Exception handlers globais — respostas de erro padronizadas em toda a API
#
# Por que intercepto aqui e não deixo o FastAPI tratar sozinho?
# Porque o formato padrão do FastAPI é diferente do meu ErrorResponse.
# O frontend precisa de um contrato único — independente do endpoint que falhou.
# ─────────────────────────────────────────────────────────────────────────────

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Intercepto todas as HTTPException lançadas nos services e routers.
    404, 409, 400 — todos chegam aqui com o mesmo formato de saída.
    """
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
    """
    Erros de validação do Pydantic — 422 com detalhes de cada campo inválido.
    Útil para o frontend mostrar erros inline nos formulários.
    """
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
    """
    Captura qualquer erro não tratado — última linha de defesa.
    Nunca exponho stack trace em produção.
    O erro real aparece no log do servidor para investigação.
    """
    logger.exception("Erro não tratado: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status_code": 500,
            "error": "internal_server_error",
            "message": "Erro interno — contate o suporte",
        },
    )


def _status_para_tipo(status_code: int) -> str:
    """Converte status code em string legível para o campo 'error'."""
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
    """
    Verifico a conexão com o banco antes de aceitar qualquer requisição.
    Se o banco estiver inacessível prefiro abortar do que servir erros 500
    para todos os clientes — fail fast é melhor que degradação silenciosa.
    """
    logger.info("Iniciando aplicação [%s]...", settings.ENVIRONMENT)
    if not check_db_connection():
        logger.critical("Banco de dados inacessível. Abortando.")
        raise RuntimeError("Database unreachable on startup.")
    logger.info("Banco de dados OK.")
    logger.info("Aplicação pronta para receber requisições.")


# ─────────────────────────────────────────────────────────────────────────────
# Routers — todos prefixados com /api/v1
# ─────────────────────────────────────────────────────────────────────────────

API_PREFIX = "/api/v1"

app.include_router(product_router,   prefix=API_PREFIX)
app.include_router(order_router,     prefix=API_PREFIX)
app.include_router(log_router,       prefix=API_PREFIX)
app.include_router(dashboard_router, prefix=API_PREFIX)


# ─────────────────────────────────────────────────────────────────────────────
# Health check — usado pelo Docker healthcheck e pelo load balancer
#
# Retorna status real do banco — não só "ok" estático.
# Se o banco cair depois do startup, o health reflete isso imediatamente.
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["Infra"], summary="Status da aplicação e do banco")
def health_check() -> dict:
    db_ok = check_db_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "up" if db_ok else "down",
        "environment": settings.ENVIRONMENT,
    }