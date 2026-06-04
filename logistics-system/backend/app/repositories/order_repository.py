"""
OrderRepository — toda query de pedido passa por aqui.

Carrego os itens junto com o pedido para evitar N+1 queries.
"""

from datetime import datetime, timezone

from sqlalchemy import cast, Date, func, select, update
from sqlalchemy.orm import Session, joinedload

from app.models.order import Pedido


class OrderRepository:

    def __init__(self, db: Session) -> None:
        self.db = db

    def criar(self, pedido: Pedido) -> Pedido:
        self.db.add(pedido)
        self.db.flush()
        self.db.refresh(pedido)
        return pedido

    def buscar_por_id(self, pedido_id: int) -> Pedido | None:
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

    def atualizar_status(self, pedido_id: int, novo_status: str) -> Pedido | None:
        """
        CORRIGIDO: busca o objeto e aplica setattr — mais seguro que returning().
        """
        pedido = self.db.get(Pedido, pedido_id)
        if not pedido:
            return None
        pedido.status = novo_status
        self.db.flush()
        self.db.refresh(pedido)
        return pedido

    def contar_pedidos_hoje(self) -> int:
        """
        CORRIGIDO: usa UTC explícito — evita bug de timezone entre
        servidor e banco quando rodam em fusos diferentes.
        """
        hoje = datetime.now(timezone.utc).date()
        stmt = select(func.count()).select_from(Pedido).where(
            cast(Pedido.data_criacao, Date) == hoje
        )
        return self.db.scalar(stmt) or 0