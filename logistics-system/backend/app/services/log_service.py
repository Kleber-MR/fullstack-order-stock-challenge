"""
LogService — geração de logs de auditoria.

Crio esse service primeiro porque todos os outros dependem dele.
Todo service que modifica dados chama o LogService para registrar o que aconteceu.
Assim garanto que nenhuma operação importante passa sem rastro.
"""

import json
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.log import Log
from app.repositories.log_repository import LogRepository
from app.schemas.log import LogResponse
from app.schemas.common import PaginatedResponse


class LogService:

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = LogRepository(db)

    def registrar(
        self,
        entidade_tipo: str,
        entidade_id: UUID,
        acao: str,
        detalhes: dict | None = None,
    ) -> Log:
        """
        Registro central de auditoria — chamo isso em toda operação relevante.
        detalhes aceita um dict e eu converto pra JSON — quem chama não precisa saber disso.
        Não commito aqui — quem controla a transação é o service pai.
        """
        log = Log(
            entidade_tipo=entidade_tipo,
            entidade_id=entidade_id,
            acao=acao,
            detalhes=json.dumps(detalhes, default=str) if detalhes else None,
        )
        return self.repo.registrar(log)

    def listar(
        self,
        skip: int = 0,
        limit: int = 50,
        entidade_tipo: str | None = None,
        entidade_id: UUID | None = None,
    ) -> PaginatedResponse[LogResponse]:
        """
        Listagem de logs com filtros opcionais.
        Útil para auditoria e rastreamento de operações por entidade.
        """
        logs, total = self.repo.listar(
            skip=skip,
            limit=limit,
            entidade_tipo=entidade_tipo,
            entidade_id=entidade_id,
        )
        return PaginatedResponse(
            items=[LogResponse.model_validate(log) for log in logs],
            total_count=total,
            skip=skip,
            limit=limit,
        )