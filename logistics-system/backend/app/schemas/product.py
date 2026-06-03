"""
Schemas de Produto — validação de entrada e serialização de saída.

ProductCreate: o que eu espero receber na criação.
ProductUpdate: campos opcionais para atualização parcial (PATCH).
ProductResponse: o que eu devolvo — nunca exponho campos internos do banco.
ProductLowStockResponse: resposta específica para alerta de estoque baixo.
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.common import BaseResponse


class ProductCreate(BaseModel):
    """
    O que eu espero receber quando alguém cria um produto.
    Coloco restrições aqui para não deixar lixo chegar no banco.
    """

    nome: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Nome do produto",
        examples=["Camiseta Básica Preta"],
    )

    sku: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Código único de identificação do produto",
        examples=["CAM-001-P"],
    )

    preco: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        description="Preço deve ser maior que zero",
        examples=[49.90],
    )

    quantidade_estoque: int = Field(
        default=0,
        ge=0,
        description="Estoque não pode ser negativo",
        examples=[100],
    )

    @field_validator("sku")
    @classmethod
    def sku_formato_valido(cls, v: str) -> str:
        """
        SKU precisa estar no formato esperado: letras, números e hífens.
        Rejeito espaços e caracteres especiais antes de qualquer coisa.
        """
        import re
        if not re.match(r"^[A-Za-z0-9\-]+$", v):
            raise ValueError("SKU só pode conter letras, números e hífens")
        return v.upper()  # normalizo para maiúsculo — padrão da empresa

    @field_validator("nome")
    @classmethod
    def nome_sem_espacos_extras(cls, v: str) -> str:
        """Limpo espaços nas pontas — dado limpo desde a entrada."""
        return v.strip()


class ProductUpdate(BaseModel):
    """
    Para atualização parcial (PATCH) todos os campos são opcionais.
    O cliente manda só o que quer alterar.
    Não permito atualizar o SKU depois de criado — ele é imutável.
    """

    nome: str | None = Field(None, min_length=2, max_length=255)
    preco: Decimal | None = Field(None, gt=0, decimal_places=2)
    quantidade_estoque: int | None = Field(None, ge=0)

    @model_validator(mode="after")
    def pelo_menos_um_campo(self) -> "ProductUpdate":
        """
        Não faz sentido receber um PATCH sem nenhum campo.
        Melhor rejeitar cedo do que processar uma operação vazia.
        """
        valores = [self.nome, self.preco, self.quantidade_estoque]
        if all(v is None for v in valores):
            raise ValueError("Pelo menos um campo deve ser informado para atualização")
        return self


class ProductResponse(BaseResponse):
    """
    O que eu devolvo para quem consulta um produto.
    Incluo data_criacao para auditoria e controle.
    """

    id: UUID
    nome: str
    sku: str
    preco: Decimal
    quantidade_estoque: int
    data_criacao: datetime


class ProductLowStockResponse(BaseResponse):
    """
    Schema específico para o endpoint de alerta de estoque baixo.
    Incluo o threshold no retorno para o frontend exibir corretamente.
    """

    id: UUID
    nome: str
    sku: str
    quantidade_estoque: int
    threshold: int  # limite que foi usado na consulta