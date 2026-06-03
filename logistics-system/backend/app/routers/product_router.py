"""
Router de Produtos — endpoints CRUD + endpoints extras de negócio.

O router não tem lógica de negócio — ele só:
  1. Recebe a requisição
  2. Valida os dados de entrada (o schema faz isso automaticamente)
  3. Chama o service correto
  4. Devolve a resposta

Se eu precisar mudar uma regra de negócio, não toco aqui.
Se eu precisar mudar a rota ou o status code, não toco no service.
"""

from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.product import (
    ProductCreate,
    ProductLowStockResponse,
    ProductResponse,
    ProductUpdate,
)
from app.services.product_service import ProductService


router = APIRouter(prefix="/products", tags=["Produtos"])


def get_service(db: Session = Depends(get_db)) -> ProductService:
    """
    Função de dependência — o FastAPI injeta a sessão do banco automaticamente.
    Centralizo a criação do service aqui para não repetir em cada endpoint.
    """
    return ProductService(db)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar produto",
    description="Cria um novo produto. SKU deve ser único no sistema.",
)
def criar_produto(
    dados: ProductCreate,
    service: ProductService = Depends(get_service),
) -> ProductResponse:
    """
    201 em criação bem-sucedida — não uso 200 aqui, semântica importa.
    O schema valida os dados antes de chegar no service.
    409 se SKU duplicado — tratado no service.
    """
    return service.criar(dados)


@router.get(
    "",
    response_model=PaginatedResponse[ProductResponse],
    summary="Listar produtos",
    description="Lista produtos com filtros opcionais e paginação.",
)
def listar_produtos(
    skip: int = Query(default=0, ge=0, description="Registros a pular"),
    limit: int = Query(default=20, ge=1, le=100, description="Máximo de registros"),
    search: str | None = Query(default=None, description="Busca por nome ou SKU"),
    min_price: Decimal | None = Query(default=None, gt=0, description="Preço mínimo"),
    max_price: Decimal | None = Query(default=None, gt=0, description="Preço máximo"),
    in_stock: bool | None = Query(default=None, description="Apenas com estoque?"),
    service: ProductService = Depends(get_service),
) -> PaginatedResponse[ProductResponse]:
    """
    Query params opcionais — o service lida com None corretamente.
    Limite máximo de 100 por requisição — proteção contra queries pesadas.
    """
    return service.listar(
        skip=skip,
        limit=limit,
        search=search,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
    )


@router.get(
    "/low-stock",
    response_model=list[ProductLowStockResponse],
    summary="Produtos com estoque baixo",
    description="Lista produtos abaixo do threshold configurável.",
)
def listar_estoque_baixo(
    threshold: int = Query(default=10, ge=1, description="Limite de estoque baixo"),
    service: ProductService = Depends(get_service),
) -> list[ProductLowStockResponse]:
    """
    Essa rota vem ANTES de /{produto_id} — se viesse depois, o FastAPI
    tentaria converter 'low-stock' como UUID e daria 422.
    Ordem de declaração de rotas importa no FastAPI.
    """
    return service.listar_estoque_baixo(threshold)


@router.get(
    "/{produto_id}",
    response_model=ProductResponse,
    summary="Buscar produto por ID",
)
def buscar_produto(
    produto_id: UUID,
    service: ProductService = Depends(get_service),
) -> ProductResponse:
    """
    UUID como path param — o FastAPI já valida o formato antes de chegar aqui.
    404 se não encontrado — tratado no service.
    """
    return service.buscar_por_id(produto_id)


@router.patch(
    "/{produto_id}",
    response_model=ProductResponse,
    summary="Atualizar produto parcialmente",
    description="Atualiza apenas os campos enviados. SKU não pode ser alterado.",
)
def atualizar_produto(
    produto_id: UUID,
    dados: ProductUpdate,
    service: ProductService = Depends(get_service),
) -> ProductResponse:
    """
    PATCH para atualização parcial — não exige todos os campos.
    PUT seria para substituição completa — não é o caso aqui.
    """
    return service.atualizar(produto_id, dados)