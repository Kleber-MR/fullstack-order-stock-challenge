"""
Ponto de entrada dos schemas.

Qualquer lugar do projeto importa assim:
    from app.schemas import ProductCreate, OrderResponse

Sem precisar saber em qual arquivo interno cada classe está.
Se eu reorganizar os arquivos internos, nenhum import externo quebra.
"""

from app.schemas.common import (
    BaseResponse,
    DashboardResponse,
    ErrorResponse,
    PaginatedResponse,
)
from app.schemas.log import LogResponse
from app.schemas.order import (
    ItemPedidoCreate,
    ItemPedidoResponse,
    OrderCreate,
    OrderResponse,
)
from app.schemas.product import (
    ProductCreate,
    ProductLowStockResponse,
    ProductResponse,
    ProductUpdate,
)

__all__ = [
    # common
    "BaseResponse",
    "PaginatedResponse",
    "ErrorResponse",
    "DashboardResponse",
    # product
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "ProductLowStockResponse",
    # order
    "ItemPedidoCreate",
    "ItemPedidoResponse",
    "OrderCreate",
    "OrderResponse",
    # log
    "LogResponse",
]