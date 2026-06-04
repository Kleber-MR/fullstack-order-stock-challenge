"""
Schemas de Produto — alinhado com model real.

  - id: int (não UUID)
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.common import BaseResponse


class ProductCreate(BaseModel):
    """O que eu espero receber quando alguém cria um produto."""

    nome: str = Field(..., min_length=2, max_length=255, examples=["Camiseta Básica Preta"])
    sku: str = Field(..., min_length=3, max_length=100, examples=["CAM-001-P"])
    preco: Decimal = Field(..., gt=0, decimal_places=2, examples=[49.90])
    quantidade_estoque: int = Field(default=0, ge=0, examples=[100])

    @field_validator("sku")
    @classmethod
    def sku_formato_valido(cls, v: str) -> str:
        import re
        if not re.match(r"^[A-Za-z0-9\-]+$", v):
            raise ValueError("SKU só pode conter letras, números e hífens")
        return v.upper()

    @field_validator("nome")
    @classmethod
    def nome_sem_espacos_extras(cls, v: str) -> str:
        return v.strip()


class ProductUpdate(BaseModel):
    """Para atualização parcial (PATCH) todos os campos são opcionais."""

    nome: str | None = Field(None, min_length=2, max_length=255)
    preco: Decimal | None = Field(None, gt=0, decimal_places=2)
    quantidade_estoque: int | None = Field(None, ge=0)

    @model_validator(mode="after")
    def pelo_menos_um_campo(self) -> "ProductUpdate":
        if all(v is None for v in [self.nome, self.preco, self.quantidade_estoque]):
            raise ValueError("Pelo menos um campo deve ser informado para atualização")
        return self


class ProductResponse(BaseResponse):
    """O que eu devolvo para quem consulta um produto."""

    id: int
    nome: str
    sku: str
    preco: Decimal
    quantidade_estoque: int
    data_criacao: datetime


class ProductLowStockResponse(BaseResponse):
    """Schema específico para o endpoint de alerta de estoque baixo."""

    id: int
    nome: str
    sku: str
    quantidade_estoque: int
    threshold: int