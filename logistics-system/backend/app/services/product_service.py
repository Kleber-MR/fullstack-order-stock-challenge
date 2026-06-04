"""
ProductService — regras de negócio de produto.

Alinhado com os models reais:
  - Product (não Produto)
  - id: int (não UUID)
  - Log com acao/detalhe (não entidade_tipo/detalhes)
"""

from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.schemas.common import DashboardResponse, PaginatedResponse
from app.schemas.product import (
    ProductCreate,
    ProductLowStockResponse,
    ProductResponse,
    ProductUpdate,
)
from app.services.log_service import LogService


class ProductService:

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ProductRepository(db)
        self.log = LogService(db)

    def criar(self, dados: ProductCreate) -> ProductResponse:
        """
        Crio produto validando unicidade do SKU antes de qualquer INSERT.
        Se o SKU já existe lanço 409 — conflito de recurso.
        """
        produto_existente = self.repo.buscar_por_sku(dados.sku)
        if produto_existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Já existe um produto com o SKU '{dados.sku}'",
            )

        product = Product(
            nome=dados.nome,
            sku=dados.sku.upper(),
            preco=dados.preco,
            quantidade_estoque=dados.quantidade_estoque,
        )

        product = self.repo.criar(product)

        self.log.registrar(
            acao="produto_criado",
            detalhe=f"Produto criado: id={product.id} sku={product.sku} preco={product.preco}",
        )

        self.db.commit()
        self.db.refresh(product)
        return ProductResponse.model_validate(product)

    def buscar_por_id(self, product_id: int) -> ProductResponse:
        """Busca por ID com 404 claro se não encontrar."""
        product = self.repo.buscar_por_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produto '{product_id}' não encontrado",
            )
        return ProductResponse.model_validate(product)

    def listar(
        self,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        in_stock: bool | None = None,
    ) -> PaginatedResponse[ProductResponse]:
        """Listagem com filtros compostos e paginação."""
        products, total = self.repo.listar(
            skip=skip,
            limit=limit,
            search=search,
            min_price=min_price,
            max_price=max_price,
            in_stock=in_stock,
        )
        return PaginatedResponse(
            items=[ProductResponse.model_validate(p) for p in products],
            total_count=total,
            skip=skip,
            limit=limit,
        )

    def atualizar(self, product_id: int, dados: ProductUpdate) -> ProductResponse:
        """Atualização parcial — só processo os campos que vieram preenchidos."""
        product_atual = self.repo.buscar_por_id(product_id)
        if not product_atual:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produto '{product_id}' não encontrado",
            )

        campos = dados.model_dump(exclude_none=True)
        product_atualizado = self.repo.atualizar(product_id, campos)

        self.log.registrar(
            acao="produto_atualizado",
            detalhe=f"Produto atualizado: id={product_id} campos={list(campos.keys())}",
        )

        self.db.commit()
        self.db.refresh(product_atualizado)
        return ProductResponse.model_validate(product_atualizado)

    def listar_estoque_baixo(self, threshold: int = 10) -> list[ProductLowStockResponse]:
        """Alerta de estoque baixo com threshold configurável."""
        if threshold < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Threshold não pode ser negativo",
            )

        products = self.repo.listar_estoque_baixo(threshold)
        return [
            ProductLowStockResponse(
                id=p.id,
                nome=p.nome,
                sku=p.sku,
                quantidade_estoque=p.quantidade_estoque,
                threshold=threshold,
            )
            for p in products
        ]