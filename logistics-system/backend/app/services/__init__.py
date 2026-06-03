"""
Ponto de entrada dos services.

Qualquer lugar do projeto importa assim:
    from app.services import ProductService, OrderService

Sem precisar saber em qual arquivo interno cada classe está.
"""

from app.services.dashboard_service import DashboardService
from app.services.log_service import LogService
from app.services.order_service import OrderService
from app.services.product_service import ProductService

__all__ = [
    "ProductService",
    "OrderService",
    "LogService",
    "DashboardService",
]