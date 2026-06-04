"""
ProductRepository — toda query de produto passa por aqui.

Mantém os métodos originais e adiciona os necessários para o service.
"""

from decimal import Decimal

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.models.product import Product


class ProductRepository:

    def __init__(self, db: Session) -> None:
        self.db = db

    # ── Métodos originais mantidos ────────────────────────────────────────────

    def get_all(self) -> list[Product]:
        return list(self.db.scalars(select(Product)).all())

    def get_by_id(self, product_id: int) -> Product | None:
        return self.db.scalars(
            select(Product).where(Product.id == product_id)
        ).first()

    def get_by_sku(self, sku: str) -> Product | None:
        return self.db.scalars(
            select(Product).where(Product.sku == sku)
        ).first()

    def create(self, product: Product) -> Product:
        self.db.add(product)
        self.db.flush()
        return product

    def update(self, product: Product) -> Product:
        self.db.flush()
        return product

    def delete(self, product: Product) -> None:
        self.db.delete(product)
        self.db.flush()

    def count_low_stock(self, threshold: int = 5) -> int:
        stmt = select(func.count(Product.id)).where(
            Product.quantidade_estoque <= threshold
        )
        return int(self.db.scalar(stmt))

    # ── Métodos adicionados para o service ────────────────────────────────────

    def criar(self, product: Product) -> Product:
        self.db.add(product)
        self.db.flush()
        self.db.refresh(product)
        return product

    def buscar_por_id(self, product_id: int) -> Product | None:
        return self.get_by_id(product_id)

    def buscar_por_sku(self, sku: str) -> Product | None:
        return self.get_by_sku(sku)

    def listar(
        self,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        in_stock: bool | None = None,
    ) -> tuple[list[Product], int]:
        stmt = select(Product)
        count_stmt = select(func.count()).select_from(Product)

        if search:
            filtro = (
                Product.nome.ilike(f"%{search}%") |
                Product.sku.ilike(f"%{search}%")
            )
            stmt = stmt.where(filtro)
            count_stmt = count_stmt.where(filtro)

        if min_price is not None:
            stmt = stmt.where(Product.preco >= min_price)
            count_stmt = count_stmt.where(Product.preco >= min_price)

        if max_price is not None:
            stmt = stmt.where(Product.preco <= max_price)
            count_stmt = count_stmt.where(Product.preco <= max_price)

        if in_stock is True:
            stmt = stmt.where(Product.quantidade_estoque > 0)
            count_stmt = count_stmt.where(Product.quantidade_estoque > 0)
        elif in_stock is False:
            stmt = stmt.where(Product.quantidade_estoque == 0)
            count_stmt = count_stmt.where(Product.quantidade_estoque == 0)

        total = self.db.scalar(count_stmt) or 0
        products = self.db.scalars(
            stmt.order_by(Product.data_criacao.desc()).offset(skip).limit(limit)
        ).all()

        return list(products), total

    def listar_estoque_baixo(self, threshold: int) -> list[Product]:
        stmt = (
            select(Product)
            .where(Product.quantidade_estoque <= threshold)
            .order_by(Product.quantidade_estoque.asc())
        )
        return list(self.db.scalars(stmt).all())

    def atualizar(self, product_id: int, dados: dict) -> Product | None:
        stmt = (
            update(Product)
            .where(Product.id == product_id)
            .values(**dados)
            .returning(Product)
        )
        return self.db.scalar(stmt)

    def decrementar_estoque(self, product_id: int, quantidade: int) -> Product | None:
        stmt = (
            update(Product)
            .where(
                Product.id == product_id,
                Product.quantidade_estoque >= quantidade,
            )
            .values(quantidade_estoque=Product.quantidade_estoque - quantidade)
            .returning(Product)
        )
        return self.db.scalar(stmt)

    def incrementar_estoque(self, product_id: int, quantidade: int) -> Product | None:
        stmt = (
            update(Product)
            .where(Product.id == product_id)
            .values(quantidade_estoque=Product.quantidade_estoque + quantidade)
            .returning(Product)
        )
        return self.db.scalar(stmt)

    def calcular_valor_total_estoque(self) -> Decimal:
        stmt = select(func.sum(Product.preco * Product.quantidade_estoque))
        return self.db.scalar(stmt) or Decimal("0")

    def contar_estoque_critico(self, threshold: int = 10) -> int:
        stmt = select(func.count()).select_from(Product).where(
            Product.quantidade_estoque <= threshold
        )
        return self.db.scalar(stmt) or 0