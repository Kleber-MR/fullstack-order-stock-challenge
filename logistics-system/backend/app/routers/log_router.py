"""
Router de Logs — somente leitura.

Logs são imutáveis — não existe POST, PATCH ou DELETE aqui.
Só expongo endpoints de consulta para auditoria e rastreamento.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.log import LogResponse
from app.services.log_service import LogService


router = APIRouter(prefix="/logs", tags=["Logs"])


def get_service(db: Session = Depends(get_db)) -> LogService:
    return LogService(db)


@router.get(
    "",
    response_model=PaginatedResponse[LogResponse],
    summary="Listar logs de auditoria",
    description=(
        "Lista o histórico de operações do sistema. "
        "Filtrável por tipo de entidade e ID específico."
    ),
)
def listar_logs(
    skip: int = Query(default=0, ge=0, description="Registros a pular"),
    limit: int = Query(default=50, ge=1, le=200, description="Máximo de registros"),
    entidade_tipo: str | None = Query(
        default=None,
        description="Filtrar por tipo: 'produto', 'pedido'",
    ),
    entidade_id: UUID | None = Query(
        default=None,
        description="Filtrar por ID específico de uma entidade",
    ),
    service: LogService = Depends(get_service),
) -> PaginatedResponse[LogResponse]:
    """
    Limite de 200 por requisição — logs podem ser muitos.
    Filtrar por entidade_id é útil para ver o histórico completo de um produto.
    """
    return service.listar(
        skip=skip,
        limit=limit,
        entidade_tipo=entidade_tipo,
        entidade_id=entidade_id,
    )