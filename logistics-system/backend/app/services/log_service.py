"""
LogService — geração de logs de auditoria.

Alinhado com o model real:
  - acao: LogAction (enum)
  - detalhe: str (texto simples)
"""

from sqlalchemy.orm import Session

from app.models.log import Log, LogAction
from app.repositories.log_repository import LogRepository
from app.schemas.log import LogResponse
from app.schemas.common import PaginatedResponse


class LogService:

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = LogRepository(db)

    def registrar(self, acao: str, detalhe: str) -> Log:
        """
        Registro central de auditoria.
        acao deve ser um valor válido do enum LogAction.
        detalhe é uma string descrevendo o que aconteceu.
        Não commito aqui — quem controla a transação é o service pai.
        """
        log = Log(
            acao=LogAction(acao),
            detalhe=detalhe,
        )
        return self.repo.registrar(log)

    def listar(
        self,
        skip: int = 0,
        limit: int = 50,
        entidade_tipo: str | None = None,
        entidade_id: int | None = None,
    ) -> PaginatedResponse[LogResponse]:
        """
        Listagem de logs — filtros opcionais ignorados pois o model
        não tem entidade_tipo/entidade_id. Filtra só por paginação.
        """
        logs, total = self.repo.listar(skip=skip, limit=limit)
        return PaginatedResponse(
            items=[LogResponse.model_validate(log) for log in logs],
            total_count=total,
            skip=skip,
            limit=limit,
        )