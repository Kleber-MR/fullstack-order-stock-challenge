"""
Schemas compartilhados — reutilizados em toda a API.

BaseResponse: configuração base para todos os schemas de resposta.
PaginatedResponse: genérico para qualquer listagem paginada.
ErrorResponse: formato padrão de erro — o frontend sempre sabe o que esperar.
DashboardResponse: snapshot do sistema para a tela de gestão.
"""

from decimal import Decimal
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict


T = TypeVar("T")


class BaseResponse(BaseModel):
    """
    Todo schema de resposta herda daqui.
    from_attributes permite converter objetos SQLAlchemy direto em schema
    sem precisar montar dicionário na mão.
    """
    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Envolve qualquer lista de resultados com metadados de paginação.
    O frontend usa total_count para calcular quantas páginas existem.

    Uso:
        PaginatedResponse[ProductResponse]
        PaginatedResponse[OrderResponse]
    """
    items: list[T]
    total_count: int
    skip: int
    limit: int


class ErrorResponse(BaseModel):
    """
    Todo erro da API segue esse formato — o frontend sabe sempre o que esperar.
    Nunca exponho stack trace em produção, só em ambiente de desenvolvimento.
    """
    status_code: int
    error: str          # tipo: "not_found", "conflict", "validation_error"
    message: str        # mensagem legível para o desenvolvedor
    detail: str | None = None  # contexto adicional quando necessário


class DashboardResponse(BaseModel):
    """
    Snapshot do estado atual do sistema para a tela de gestão.
    Dados calculados no banco com queries otimizadas — não processo em Python.
    """
    total_produtos: int
    pedidos_hoje: int
    valor_total_estoque: Decimal
    itens_estoque_critico: int  # produtos abaixo do threshold padrão