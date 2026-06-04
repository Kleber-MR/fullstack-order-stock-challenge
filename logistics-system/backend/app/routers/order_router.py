"""
Router de Pedidos — criação, listagem e cancelamento.

Operações de pedido são as mais críticas do sistema.
O router só orquestra — toda regra de negócio e atomicidade está no OrderService.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.order import OrderCreate, OrderResponse
from app.services.order_service import OrderService


router = APIRouter(prefix="/orders", tags=["Pedidos"])


def get_service(db: Session = Depends(get_db)) -> OrderService:
    return OrderService(db)


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar pedido",
    description=(
        "Cria um pedido e decrementa o estoque de cada item atomicamente. "
        "Se qualquer item não tiver estoque suficiente, o pedido inteiro é rejeitado."
    ),
)
def criar_pedido(
    dados: OrderCreate,
    service: OrderService = Depends(get_service),
) -> OrderResponse:
    return service.criar(dados)


@router.get(
    "",
    response_model=PaginatedResponse[OrderResponse],
    summary="Listar pedidos",
    description="Lista todos os pedidos com paginação.",
)
def listar_pedidos(
    skip: int = Query(default=0, ge=0, description="Registros a pular"),
    limit: int = Query(default=20, ge=1, le=100, description="Máximo de registros"),
    service: OrderService = Depends(get_service),
) -> PaginatedResponse[OrderResponse]:
    return service.listar(skip=skip, limit=limit)


@router.get(
    "/{pedido_id}",
    response_model=OrderResponse,
    summary="Buscar pedido por ID",
)
def buscar_pedido(
    # CORRIGIDO: int (não UUID) — a PK do model Order é Integer autoincrement
    pedido_id: int,
    service: OrderService = Depends(get_service),
) -> OrderResponse:
    return service.buscar_por_id(pedido_id)


@router.patch(
    "/{pedido_id}/cancel",
    response_model=OrderResponse,
    summary="Cancelar pedido",
    description=(
        "Cancela o pedido e estorna o estoque de cada item. "
        "Pedido já cancelado retorna 400."
    ),
)
def cancelar_pedido(
    # CORRIGIDO: int (não UUID) — a PK do model Order é Integer autoincrement
    pedido_id: int,
    service: OrderService = Depends(get_service),
) -> OrderResponse:
    return service.cancelar(pedido_id)