"""
conftest.py — configuração global dos testes.

Estratégia:
  - SQLite em memória — sem precisar de PostgreSQL rodando
  - Banco zerado a cada teste — isolamento total
  - Cliente HTTP real via TestClient do FastAPI
  - Fixtures compartilhadas entre unit e integration
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app

# ── Importa todos os models para registrar no Base.metadata ──
from app.models.product import Product  # noqa: F401
from app.models.order import Order, OrderItem  # noqa: F401
from app.models.log import Log  # noqa: F401

# ─── Banco em memória ─────────────────────────────────────────────────────────

# SQLite em memória — cada sessão de teste tem seu banco limpo
SQLITE_URL = "sqlite://"

engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  
)
# Habilito foreign keys no SQLite — desabilitado por padrão
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def setup_database():
    """
    Cria todas as tabelas antes de cada teste e apaga depois.
    autouse=True — roda automaticamente em todos os testes.
    Isso garante isolamento total — nenhum teste depende de outro.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """
    Sessão do banco para testes.
    Fecha a sessão após cada teste.
    """
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    """
    Cliente HTTP do FastAPI com o banco de teste injetado.
    Substitui o get_db real pelo get_db de teste — sem tocar no banco real.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def produto_base(client):
    """
    Cria um produto padrão e devolve os dados.
    Reutilizado nos testes de pedido — não preciso recriar em cada um.
    """
    res = client.post("/api/v1/products", json={
        "nome": "Produto Teste",
        "sku": "PROD-001",
        "preco": 50.00,
        "quantidade_estoque": 10,
    })
    assert res.status_code == 201
    return res.json()


@pytest.fixture
def produto_sem_estoque(client):
    """Produto com estoque zero — para testar bloqueio de pedido."""
    res = client.post("/api/v1/products", json={
        "nome": "Produto Sem Estoque",
        "sku": "PROD-ZERO",
        "preco": 30.00,
        "quantidade_estoque": 0,
    })
    assert res.status_code == 201
    return res.json()