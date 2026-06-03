"""
LogRepository — inserção e leitura de logs de auditoria.

Logs são imutáveis — nunca atualizo ou deleto.
Registro de auditoria só acrescenta, nunca modifica.
"""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.log import Log


class LogRepository:

    def __init__(self, db: Session) -> None:
        self.db = db

    def registrar(self, log: Log) -> Log:
        """
        Insiro o log e devolvo com o id gerado.
        Uso flush ao invés de commit — quem controla a transação é o service.
        """
        self.db.add(log)
        self.db.flush()
        self.db.refresh(log)
        return log

    def listar(
        self,
        skip: int = 0,
        limit: int = 50,
        entidade_tipo: str | None = None,
        entidade_id: UUID | None = None,
    ) -> tuple[list[Log], int]:
        """
        Listagem com filtros opcionais por entidade.
        Mais recentes primeiro — faz mais sentido para auditoria.
        """
        stmt = select(Log)
        count_stmt = select(func.count()).select_from(Log)

        if entidade_tipo:
            stmt = stmt.where(Log.entidade_tipo == entidade_tipo)
            count_stmt = count_stmt.where(Log.entidade_tipo == entidade_tipo)

        if entidade_id:
            stmt = stmt.where(Log.entidade_id == entidade_id)
            count_stmt = count_stmt.where(Log.entidade_id == entidade_id)

        total = self.db.scalar(count_stmt) or 0
        logs = self.db.scalars(
            stmt.order_by(Log.criado_em.desc()).offset(skip).limit(limit)
        ).all()

        return list(logs), total