"""
Ponto de entrada dos routers.

O main.py importa só daqui — não precisa conhecer cada arquivo interno.
Para adicionar um novo router basta incluir aqui e registrar no main.py.
"""

from app.routers.dashboard_router import router as dashboard_router
from app.routers.log_router import router as log_router
from app.routers.order_router import router as order_router
from app.routers.product_router import router as product_router

__all__ = [
    "product_router",
    "order_router",
    "log_router",
    "dashboard_router",
]