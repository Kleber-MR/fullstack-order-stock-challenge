import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.settings import settings

logger = logging.getLogger(__name__)

# ─── Engine ───────────────────────────────────────────────────────────────────

engine = create_engine(
    settings.DATABASE_URL_str,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    echo=settings.DB_ECHO,
    connect_args={"connect_timeout": 10},
)


@event.listens_for(engine, "connect")
def _on_connect(dbapi_conn, _record) -> None:
    logger.debug("Nova conexão aberta com o banco de dados.")


# ─── Session factory ──────────────────────────────────────────────────────────

SessionLocal: sessionmaker[Session] = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# ─── Base declarativa (SQLAlchemy 2.x) ────────────────────────────────────────

class Base(DeclarativeBase):
    """Base para todos os models SQLAlchemy."""


# ─── Dependência FastAPI ──────────────────────────────────────────────────────

def get_db() -> Generator[Session, None, None]:
    """
    Injeta sessão do banco por requisição via Depends(get_db).
    Faz commit automático no sucesso e rollback em qualquer exceção.
    """
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Erro na sessão — rollback executado.")
        raise
    finally:
        db.close()


# ─── Context manager para uso fora do ciclo HTTP ─────────────────────────────

@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Para scripts, workers e tarefas fora do FastAPI."""
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ─── Health check ─────────────────────────────────────────────────────────────

def check_db_connection() -> bool:
    """Retorna True se o banco está acessível. Usado no /health e no startup."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        logger.exception("Falha no health check do banco.")
        return False