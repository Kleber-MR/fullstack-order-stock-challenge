"""
Router de Dashboard — snapshot agregado do sistema.

Um endpoint só — devolve tudo que a tela de gestão precisa em uma chamada.
O frontend não precisa fazer múltiplas requisições para montar o dashboard.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import DashboardResponse
from app.services.dashboard_service import DashboardService


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_service(db: Session = Depends(get_db)) -> DashboardService:
    return DashboardService(db)


@router.get(
    "",
    response_model=DashboardResponse,
    summary="Resumo do sistema",
    description=(
        "Retorna snapshot com total de produtos, pedidos do dia, "
        "valor total em estoque e itens com estoque crítico."
    ),
)
def obter_resumo(
    service: DashboardService = Depends(get_service),
) -> DashboardResponse:
    """
    Todas as queries são agregadas no banco — não processo em Python.
    Uma chamada, todos os dados da tela de gestão.
    """
    return service.obter_resumo()