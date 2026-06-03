"""
DashboardService — agrega dados de múltiplos services em um snapshot.

Não acesso o banco diretamente aqui.
Chamo os métodos de dados dos outros services e monto a resposta final.
Separar isso em um service próprio evita que o router precise orquestrar múltiplas chamadas.
"""

from sqlalchemy.orm import Session

from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.common import DashboardResponse


class DashboardService:

    def __init__(self, db: Session) -> None:
        self.db = db
        self.produto_repo = ProductRepository(db)
        self.pedido_repo = OrderRepository(db)

    def obter_resumo(self) -> DashboardResponse:
        """
        Monto o resumo do dashboard com queries otimizadas no banco.
        Cada método do repository executa uma query agregada — não processo em Python.
        """

        # Busco o total de produtos com uma query de count — não trago todos os registros
        _, total_produtos = self.produto_repo.listar(skip=0, limit=1)

        return DashboardResponse(
            total_produtos=total_produtos,
            pedidos_hoje=self.pedido_repo.contar_pedidos_hoje(),
            valor_total_estoque=self.produto_repo.calcular_valor_total_estoque(),
            itens_estoque_critico=self.produto_repo.contar_estoque_critico(threshold=10),
        )