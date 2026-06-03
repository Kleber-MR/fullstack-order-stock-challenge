from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class OrderStatus(str, PyEnum):
    PENDENTE = "pendente"
    CANCELADO = "cancelado"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="order_status"),
        nullable=False,
        default=OrderStatus.PENDENTE,
    )
    total: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    data_criacao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    itens: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Order id={self.id} status={self.status} total={self.total}>"


class OrderItem(Base):
    __tablename__ = "order_items"

    __table_args__ = (
        CheckConstraint("quantidade > 0", name="ck_order_items_quantidade_positive"),
        CheckConstraint("preco_unitario > 0", name="ck_order_items_preco_positive"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    produto_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("products.id", ondelete="RESTRICT"),  # impede deleção de produto com pedido
        nullable=False,
        index=True,
    )
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    preco_unitario: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Preço no momento da compra — imutável após criação",
    )

    order: Mapped["Order"] = relationship(back_populates="itens")
    product: Mapped["Product"] = relationship(back_populates="order_items")  # type: ignore[name-defined]

    def __repr__(self) -> str:
        return (
            f"<OrderItem id={self.id} "
            f"order_id={self.order_id} "
            f"produto_id={self.produto_id} "
            f"qty={self.quantidade}>"
        )