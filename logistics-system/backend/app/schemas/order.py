"""
Schemas de Pedido — alinhado com model real.

  - id: int
  - total (não valor_total)
  - status: str
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import BaseResponse


class ItemPedidoCreate(BaseModel):
    """Cada item dentro de um pedido."""
    produto_id: int = Field(..., description="ID do produto", gt=0)
    quantidade: int = Field(..., ge=1, description="Quantidade mínima é 1")


class ItemPedidoResponse(BaseResponse):
    """
    Resposta de um item com subtotal calculado.
    preco_unitario é snapshot histórico — o preço no momento da compra.
    """
    id: int
    produto_id: int
    quantidade: int
    preco_unitario: Decimal


class OrderCreate(BaseModel):
    """Criação de pedido com lista de itens."""
    itens: list[ItemPedidoCreate] = Field(
        ...,
        min_length=1,
        description="Pedido precisa ter pelo menos 1 item",
    )

    @field_validator("itens")
    @classmethod
    def sem_produtos_duplicados(cls, v: list[ItemPedidoCreate]) -> list[ItemPedidoCreate]:
        """Não aceito o mesmo produto duas vezes no mesmo pedido."""
        ids = [item.produto_id for item in v]
        if len(ids) != len(set(ids)):
            raise ValueError("O mesmo produto não pode aparecer mais de uma vez no pedido")
        return v


class OrderResponse(BaseResponse):
    """Resposta completa do pedido com todos os itens e valor total."""
    id: int
    status: str
    itens: list[ItemPedidoResponse]
    total: Decimal
    data_criacao: datetime