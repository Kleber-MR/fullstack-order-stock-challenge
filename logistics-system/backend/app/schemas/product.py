import re
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=255)
    sku: str = Field(..., min_length=1, max_length=100)
    preco: Decimal = Field(..., gt=0, decimal_places=2)
    quantidade_estoque: int = Field(..., ge=0)

    @field_validator("nome")
    @classmethod
    def nome_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Nome não pode ser vazio ou apenas espaços.")
        return v.strip()

    @field_validator("sku")
    @classmethod
    def sku_format(cls, v: str) -> str:
        v = v.strip().upper()
        if not re.match(r"^[A-Z0-9\-_]{1,100}$", v):
            raise ValueError("SKU deve conter apenas letras, números, hífen e underscore.")
        return v


class ProductUpdate(BaseModel):
    nome: str | None = Field(None, min_length=1, max_length=255)
    preco: Decimal | None = Field(None, gt=0, decimal_places=2)
    quantidade_estoque: int | None = Field(None, ge=0)

    @field_validator("nome")
    @classmethod
    def nome_not_blank(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("Nome não pode ser vazio.")
        return v.strip() if v else v


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    sku: str
    preco: Decimal
    quantidade_estoque: int
    data_criacao: datetime


class PaginatedProducts(BaseModel):
    items: list[ProductResponse]
    total: int
    skip: int
    limit: int