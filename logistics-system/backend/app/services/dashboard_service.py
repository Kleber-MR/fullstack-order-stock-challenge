"""
DashboardService — dados agregados para a tela de gestão.

Adaptado para usar os métodos reais dos repositories
e retornar os campos que o frontend espera:
  - total_produtos
  - pedidos_hoje
  - valor_total_estoque
  - itens_estoque_critico
"""

from sqlalchemy.orm import Session

from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.common import DashboardResponse


class DashboardService:

    def __init__(self, db: Session) -> None:
        self.db = db
        self.order_repo = OrderRepository(db)
        self.product_repo = ProductRepository(db)

    def get_summary(self) -> dict:
        """Método original mantido."""
        return {
            "total_produtos": len(self.product_repo.get_all()),
            "produtos_estoque_baixo": self.product_repo.count_low_stock(),
        }

    def obter_resumo(self) -> DashboardResponse:
        """
        Retorna snapshot com os campos que o frontend espera.
        Chamado pelo dashboard_router.
        """
        _, total_produtos = self.product_repo.listar(skip=0, limit=1)

        return DashboardResponse(
            total_produtos=total_produtos,
            pedidos_hoje=self.order_repo.contar_pedidos_hoje(),
            valor_total_estoque=self.product_repo.calcular_valor_total_estoque(),
            itens_estoque_critico=self.product_repo.contar_estoque_critico(threshold=10),
        )