"""
LogRepository — inserção e leitura de logs de auditoria.

Alinhado com o model real — sem entidade_tipo/entidade_id.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.log import Log


class LogRepository:

    def __init__(self, db: Session) -> None:
        self.db = db

    def registrar(self, log: Log) -> Log:
        """
        Insiro o log e devolvo com o id gerado.
        Uso flush — quem controla a transação é o service.
        """
        self.db.add(log)
        self.db.flush()
        self.db.refresh(log)
        return log

    def listar(
        self,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Log], int]:
        """
        Listagem paginada — mais recentes primeiro.
        """
        total = self.db.scalar(
            select(func.count()).select_from(Log)
        ) or 0

        logs = self.db.scalars(
            select(Log)
            .order_by(Log.data_criacao.desc())
            .offset(skip)
            .limit(limit)
        ).all()

        return list(logs), total