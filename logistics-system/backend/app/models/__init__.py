# Models SQLAlchemy — cada arquivo mapeia uma tabela do banco.
# Importe todos os models aqui para que o Alembic os detecte nas migrações.

from app.models.product import Product
from app.models.order import Order, OrderItem, OrderStatus
from app.models.log import Log, LogAction

__all__ = [
    "Product",
    "Order",
    "OrderItem",
    "OrderStatus",
    "Log",
    "LogAction",
]