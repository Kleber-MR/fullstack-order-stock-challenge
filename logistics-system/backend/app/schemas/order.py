"""
Schemas de Pedido — validação de entrada e serialização de saída.

ItemPedidoCreate: cada item dentro de um pedido.
ItemPedidoResponse: item com subtotal calculado.
OrderCreate: criação de pedido com lista de itens.
OrderResponse: pedido completo com itens e valor total.
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.common import BaseResponse


class ItemPedidoCreate(BaseModel):
    """
    Cada item dentro de um pedido.
    Valido quantidade mínima aqui — não deixo pedido de zero unidades entrar.
    """
    produto_id: int = Field(..., gt=0, description="ID do produto")
    quantidade: int = Field(..., ge=1, description="Quantidade mínima é 1")


class ItemPedidoResponse(BaseResponse):
    """
    Resposta de um item com os dados relevantes para o frontend.
    Calculo o subtotal aqui — o frontend não precisa recalcular.
    preco_unitario é snapshot histórico — o preço no momento da compra.
    """
    produto_id: int
    quantidade: int
    preco_unitario: Decimal
    subtotal: Decimal


class OrderCreate(BaseModel):
    """
    Criação de pedido com lista de itens.
    Um pedido sem itens não faz sentido — valido antes de qualquer I/O.
    """
    itens: list[ItemPedidoCreate] = Field(
        ...,
        min_length=1,
        description="Pedido precisa ter pelo menos 1 item",
    )

    @field_validator("itens")
    @classmethod
    def sem_produtos_duplicados(cls, v: list[ItemPedidoCreate]) -> list[ItemPedidoCreate]:
        """
        Não aceito o mesmo produto duas vezes no mesmo pedido.
        O cliente deve consolidar quantidades antes de enviar.
        Evito inconsistência no estoque com essa validação.
        """
        ids = [item.produto_id for item in v]
        if len(ids) != len(set(ids)):
            raise ValueError("O mesmo produto não pode aparecer mais de uma vez no pedido")
        return v


class OrderResponse(BaseResponse):
    """
    Resposta completa do pedido com todos os itens e valor total.
    O total é calculado no service e armazenado — não recalculo na serialização.
    """
    id: int
    status: str
    itens: list[ItemPedidoResponse]
    valor_total: Decimal
    data_criacao: datetime