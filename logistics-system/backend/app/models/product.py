from datetime import datetime, timezone

from sqlalchemy import DateTime, Numeric, String, Integer, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    __table_args__ = (
        CheckConstraint("preco > 0", name="ck_products_preco_positive"),
        CheckConstraint("quantidade_estoque >= 0", name="ck_products_estoque_non_negative"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    sku: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    preco: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    quantidade_estoque: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    data_criacao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relacionamento reverso — não gera coluna, só facilita queries
    order_items: Mapped[list["OrderItem"]] = relationship(  # noqa: F821
        back_populates="product",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Product id={self.id} sku={self.sku!r} estoque={self.quantidade_estoque}>"