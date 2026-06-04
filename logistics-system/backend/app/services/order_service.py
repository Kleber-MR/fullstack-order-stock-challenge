"""
OrderService — regras de negócio de pedido.

Alinhado com os models reais:
  - Order/OrderItem (não Pedido/ItemPedido)
  - id: int (não UUID)
  - total (não valor_total)
  - status: OrderStatus enum
  - Log com acao/detalhe (não entidade_tipo/detalhes)
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.order import Order, OrderItem, OrderStatus
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.common import PaginatedResponse
from app.schemas.order import OrderCreate, OrderResponse
from app.services.log_service import LogService


class OrderService:

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = OrderRepository(db)
        self.produto_repo = ProductRepository(db)
        self.log = LogService(db)

    def criar(self, dados: OrderCreate) -> OrderResponse:
        """
        Criação de pedido com atomicidade total.
        Commit só acontece quando todos os itens foram processados com sucesso.
        """
        itens_processados = []
        valor_total = 0

        for item in dados.itens:

            # ── 1. Produto existe? ────────────────────────────────────────────
            product = self.produto_repo.buscar_por_id(item.produto_id)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Produto '{item.produto_id}' não encontrado",
                )

            # ── 2. Tem estoque suficiente? ────────────────────────────────────
            if product.quantidade_estoque < item.quantidade:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Estoque insuficiente para '{product.nome}'. "
                        f"Disponível: {product.quantidade_estoque}, "
                        f"Solicitado: {item.quantidade}"
                    ),
                )

            # ── 3. Decremento atômico ─────────────────────────────────────────
            product_atualizado = self.produto_repo.decrementar_estoque(
                item.produto_id, item.quantidade
            )
            if not product_atualizado:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Estoque insuficiente para '{product.nome}' — tente novamente",
                )

            # ── 4. Snapshot do preço ──────────────────────────────────────────
            preco_unitario = float(product.preco)
            subtotal = preco_unitario * item.quantidade
            valor_total += subtotal

            itens_processados.append(
                OrderItem(
                    produto_id=item.produto_id,
                    quantidade=item.quantidade,
                    preco_unitario=preco_unitario,
                )
            )

            self.log.registrar(
                acao="movimentacao_estoque",
                detalhe=(
                    f"Estoque decrementado: produto_id={item.produto_id} "
                    f"quantidade={item.quantidade} "
                    f"estoque_restante={product_atualizado.quantidade_estoque}"
                ),
            )

        # ── 5. Crio o pedido ──────────────────────────────────────────────────
        order = Order(
            status=OrderStatus.PENDENTE,
            total=valor_total,
            itens=itens_processados,
        )
        order = self.repo.criar(order)

        self.log.registrar(
            acao="pedido_criado",
            detalhe=f"Pedido criado: id={order.id} total={valor_total} itens={len(itens_processados)}",
        )

        # ── 6. Commit — só aqui a transação fecha ─────────────────────────────
        self.db.commit()
        self.db.refresh(order)
        return OrderResponse.model_validate(order)

    def buscar_por_id(self, order_id: int) -> OrderResponse:
        """Busca com 404 claro se não encontrar."""
        order = self.repo.buscar_por_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pedido '{order_id}' não encontrado",
            )
        return OrderResponse.model_validate(order)

    def listar(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> PaginatedResponse[OrderResponse]:
        """Listagem paginada de pedidos."""
        orders, total = self.repo.listar(skip=skip, limit=limit)
        return PaginatedResponse(
            items=[OrderResponse.model_validate(o) for o in orders],
            total_count=total,
            skip=skip,
            limit=limit,
        )

    def cancelar(self, order_id: int) -> OrderResponse:
        """
        Cancelamento com estorno de estoque na mesma transação.
        """
        order = self.repo.buscar_por_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pedido '{order_id}' não encontrado",
            )

        if order.status == OrderStatus.CANCELADO:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pedido já foi cancelado",
            )

        # ── Estorno de estoque por item ───────────────────────────────────────
        for item in order.itens:
            self.produto_repo.incrementar_estoque(item.produto_id, item.quantidade)

            self.log.registrar(
                acao="movimentacao_estoque",
                detalhe=(
                    f"Estoque estornado: produto_id={item.produto_id} "
                    f"quantidade={item.quantidade} motivo=cancelamento order_id={order_id}"
                ),
            )

        order_cancelado = self.repo.atualizar_status(order_id, OrderStatus.CANCELADO)

        self.log.registrar(
            acao="pedido_cancelado",
            detalhe=f"Pedido cancelado: id={order_id} itens_estornados={len(order.itens)}",
        )

        self.db.commit()
        self.db.refresh(order_cancelado)
        return OrderResponse.model_validate(order_cancelado)