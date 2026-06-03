import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.settings import settings
from app.core.database import check_db_connection

# ─── Logging ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.DEBUG if settings.ENVIRONMENT == "development" else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

# ─── App ──────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Logistics System API",
    description="Gerenciamento de pedidos e estoque.",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

# ─── Middlewares ──────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Eventos ──────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def on_startup() -> None:
    logger.info("Iniciando aplicação [%s]...", settings.ENVIRONMENT)
    if not check_db_connection():
        logger.critical("Banco de dados inacessível. Abortando.")
        raise RuntimeError("Database unreachable on startup.")
    logger.info("Banco de dados OK.")


# ─── Routers (registrados conforme forem criados) ─────────────────────────────
# from app.routers import products, orders, logs
# app.include_router(products.router)
# app.include_router(orders.router)
# app.include_router(logs.router)


# ─── Endpoints de infraestrutura ─────────────────────────────────────────────

@app.get("/health", tags=["infra"], summary="Status da aplicação e do banco")
def health_check():
    db_ok = check_db_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "up" if db_ok else "down",
        "environment": settings.ENVIRONMENT,
    }