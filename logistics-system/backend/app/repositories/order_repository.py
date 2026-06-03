"""
OrderRepository — toda query de pedido passa por aqui.

Carrego os itens junto com o pedido para evitar N+1 queries.
"""

from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session, joinedload

from app.models.order import Pedido


class OrderRepository:

    def __init__(self, db: Session) -> None:
        self.db = db

    def criar(self, pedido: Pedido) -> Pedido:
        """
        Persisto pedido com todos os itens de uma vez.
        O relacionamento cuida de inserir os itens automaticamente.
        """
        self.db.add(pedido)
        self.db.flush()
        self.db.refresh(pedido)
        return pedido

    def buscar_por_id(self, pedido_id: UUID) -> Pedido | None:
        """
        Busco pedido já com itens carregados em uma única query (JOIN).
        Sem joinedload eu teria N+1: 1 query pro pedido + 1 por item.
        """
        stmt = (
            select(Pedido)
            .options(joinedload(Pedido.itens))
            .where(Pedido.id == pedido_id)
        )
        return self.db.scalar(stmt)

    def listar(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Pedido], int]:
        """
        Listagem paginada com itens.
        unique() é necessário quando uso joinedload com paginação
        para evitar linhas duplicadas no resultado.
        """
        total = self.db.scalar(
            select(func.count()).select_from(Pedido)
        ) or 0

        stmt = (
            select(Pedido)
            .options(joinedload(Pedido.itens))
            .order_by(Pedido.data_criacao.desc())
            .offset(skip)
            .limit(limit)
        )
        pedidos = self.db.scalars(stmt).unique().all()

        return list(pedidos), total

    def atualizar_status(self, pedido_id: UUID, novo_status: str) -> Pedido | None:
        """
        Atualizo só o status — não recarrego o objeto inteiro pra isso.
        """
        stmt = (
            update(Pedido)
            .where(Pedido.id == pedido_id)
            .values(status=novo_status)
            .returning(Pedido)
        )
        return self.db.scalar(stmt)

    def contar_pedidos_hoje(self) -> int:
        """Conta pedidos criados hoje — usado no dashboard."""
        from datetime import date
        stmt = select(func.count()).select_from(Pedido).where(
            func.date(Pedido.data_criacao) == date.today()
        )
        return self.db.scalar(stmt) or 0