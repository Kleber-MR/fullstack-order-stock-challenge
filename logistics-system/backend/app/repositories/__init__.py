"""
Ponto de entrada dos repositories.

Qualquer lugar do projeto importa assim:
    from app.repositories import ProductRepository, OrderRepository

Sem precisar saber em qual arquivo interno cada classe está.
"""

from app.repositories.log_repository import LogRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository

__all__ = [
    "ProductRepository",
    "OrderRepository",
    "LogRepository",
]