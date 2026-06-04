"""
Schema de Log — somente leitura.

Alinhado com o model real:
  - id: int
  - acao: str (valor do enum LogAction)
  - detalhe: str
  - data_criacao: datetime
"""

from datetime import datetime

from app.schemas.common import BaseResponse


class LogResponse(BaseResponse):
    """
    Resposta de log de auditoria.
    Logs são imutáveis — nunca recebo como entrada da API.
    """

    id: int
    acao: str
    detalhe: str
    data_criacao: datetime