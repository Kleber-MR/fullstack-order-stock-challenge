from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class LogAction(str, PyEnum):
    PRODUTO_CRIADO = "produto_criado"
    PRODUTO_ATUALIZADO = "produto_atualizado"
    PEDIDO_CRIADO = "pedido_criado"
    MOVIMENTACAO_ESTOQUE = "movimentacao_estoque"
    PEDIDO_CANCELADO = "pedido_cancelado"


class Log(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    acao: Mapped[LogAction] = mapped_column(
        Enum(LogAction, name="log_action"),
        nullable=False,
        index=True,
    )
    detalhe: Mapped[str] = mapped_column(Text, nullable=False)
    data_criacao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    def __repr__(self) -> str:
        return f"<Log id={self.id} acao={self.acao} data={self.data_criacao}>"