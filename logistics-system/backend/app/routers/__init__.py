from app.routers.dashboard_router import router as dashboard_router
from app.routers.log_router import router as log_router
from app.routers.order_router import router as order_router
from app.routers.product_router import router as product_router

__all__ = ["dashboard_router", "log_router", "order_router", "product_router"]