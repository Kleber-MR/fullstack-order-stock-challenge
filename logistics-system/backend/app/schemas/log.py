"""
Schema de Log — somente leitura.

Logs são gerados internamente pelo sistema — nunca recebo log como entrada.
São imutáveis por princípio: registro de auditoria não se edita, só acrescenta.
"""

from datetime import datetime
from uuid import UUID

from app.schemas.common import BaseResponse


class LogResponse(BaseResponse):
    """
    Resposta de log de auditoria.
    detalhes carrega contexto adicional em JSON — o que mudou, valores anteriores etc.
    """

    id: UUID
    entidade_tipo: str    # ex: "produto", "pedido"
    entidade_id: UUID
    acao: str             # ex: "criado", "estoque_atualizado", "pedido_cancelado"
    detalhes: str | None  # JSON stringificado com contexto adicional
    criado_em: datetime