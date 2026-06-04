"""
OrderRepository — mantém métodos originais e adiciona os necessários.
"""

from datetime import date

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session, selectinload, joinedload

from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product


class OrderRepository:

    def __init__(self, db: Session) -> None:
        self.db = db

    # ── Métodos originais mantidos ────────────────────────────────────────────

    def get_all(self) -> list[Order]:
        stmt = select(Order).options(selectinload(Order.itens))
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, order_id: int) -> Order | None:
        stmt = (
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.itens))
        )
        return self.db.scalars(stmt).first()

    def create(self, order: Order) -> Order:
        self.db.add(order)
        self.db.flush()
        return order

    def delete(self, order: Order) -> None:
        self.db.delete(order)
        self.db.flush()

    def update_status(self, order: Order, status: OrderStatus) -> Order:
        order.status = status
        self.db.flush()
        return order

    def count_by_status(self) -> dict[str, int]:
        stmt = select(Order.status, func.count(Order.id)).group_by(Order.status)
        rows = self.db.execute(stmt).all()
        return {row[0].value: row[1] for row in rows}

    def sum_total(self) -> float:
        stmt = select(func.coalesce(func.sum(Order.total), 0)).where(
            Order.status != OrderStatus.CANCELADO
        )
        return float(self.db.scalar(stmt))

    # ── Métodos adicionados para o service ────────────────────────────────────

    def criar(self, order: Order) -> Order:
        """Alias de create com refresh."""
        self.db.add(order)
        self.db.flush()
        self.db.refresh(order)
        return order

    def buscar_por_id(self, order_id: int) -> Order | None:
        """Alias de get_by_id com joinedload."""
        return self.get_by_id(order_id)

    def listar(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Order], int]:
        """Listagem paginada com total."""
        total = self.db.scalar(
            select(func.count()).select_from(Order)
        ) or 0

        stmt = (
            select(Order)
            .options(selectinload(Order.itens))
            .order_by(Order.data_criacao.desc())
            .offset(skip)
            .limit(limit)
        )
        orders = self.db.scalars(stmt).unique().all()
        return list(orders), total

    def atualizar_status(self, order_id: int, novo_status: OrderStatus) -> Order | None:
        """Atualiza status por ID."""
        stmt = (
            update(Order)
            .where(Order.id == order_id)
            .values(status=novo_status)
            .returning(Order)
        )
        return self.db.scalar(stmt)

    def contar_pedidos_hoje(self) -> int:
        """Conta pedidos criados hoje — usado no dashboard."""
        stmt = select(func.count()).select_from(Order).where(
            func.date(Order.data_criacao) == date.today()
        )
        return self.db.scalar(stmt) or 0