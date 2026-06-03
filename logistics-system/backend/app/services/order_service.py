"""
OrderService — regras de negócio de pedido.

Esse é o service mais crítico do sistema.
Criação de pedido é uma operação atômica — ou tudo acontece ou nada acontece.

Fluxo de criação:
  1. Verifico se todos os produtos existem
  2. Verifico se todos têm estoque suficiente
  3. Decremento o estoque de cada item atomicamente
  4. Calculo o valor total com o preço atual (snapshot)
  5. Crio o pedido com os itens
  6. Registro o log
  7. Commit — só aqui a transação fecha

Se qualquer etapa falhar, o rollback desfaz tudo.
O cliente nunca vê um pedido criado com estoque inconsistente.
"""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.order import ItemPedido, Pedido
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.common import PaginatedResponse
from app.schemas.order import OrderCreate, OrderResponse
from app.services.log_service import LogService


class OrderService:

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = OrderRepository(db)
        self.produto_repo = ProductRepository(db)  # preciso do produto para estoque e preço
        self.log = LogService(db)

    def criar(self, dados: OrderCreate) -> OrderResponse:
        """
        Criação de pedido com atomicidade total.

        Por que uso flush() e não commit() durante o loop?
        Porque se o terceiro item falhar, o rollback desfaz os dois primeiros também.
        O commit só acontece quando TODOS os itens foram processados com sucesso.
        """

        itens_processados = []
        valor_total = 0

        for item in dados.itens:

            # ── 1. Produto existe? ────────────────────────────────────────────
            produto = self.produto_repo.buscar_por_id(item.produto_id)
            if not produto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Produto '{item.produto_id}' não encontrado",
                )

            # ── 2. Tem estoque suficiente? ────────────────────────────────────
            # Faço essa checagem antes do decremento para dar erro mais claro
            if produto.quantidade_estoque < item.quantidade:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Estoque insuficiente para '{produto.nome}'. "
                        f"Disponível: {produto.quantidade_estoque}, "
                        f"Solicitado: {item.quantidade}"
                    ),
                )

            # ── 3. Decremento atômico ─────────────────────────────────────────
            # O WHERE no UPDATE garante que não vai a zero mesmo com requisições simultâneas
            # Se retornar None, outro pedido chegou antes e consumiu o estoque
            produto_atualizado = self.produto_repo.decrementar_estoque(
                item.produto_id, item.quantidade
            )
            if not produto_atualizado:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Estoque insuficiente para '{produto.nome}' — tente novamente",
                )

            # ── 4. Snapshot do preço ──────────────────────────────────────────
            # Salvo o preço atual no item — se o produto mudar de preço amanhã,
            # o histórico desse pedido continua correto
            preco_unitario = produto.preco
            subtotal = preco_unitario * item.quantidade
            valor_total += subtotal

            itens_processados.append(
                ItemPedido(
                    produto_id=item.produto_id,
                    quantidade=item.quantidade,
                    preco_unitario=preco_unitario,
                    subtotal=subtotal,
                )
            )

            # Log de baixa de estoque por item — rastreio cada movimentação
            self.log.registrar(
                entidade_tipo="produto",
                entidade_id=item.produto_id,
                acao="estoque_decrementado",
                detalhes={
                    "quantidade_decrementada": item.quantidade,
                    "estoque_restante": produto_atualizado.quantidade_estoque,
                    "motivo": "criacao_pedido",
                },
            )

        # ── 5. Crio o pedido com todos os itens ──────────────────────────────
        pedido = Pedido(
            status="pendente",
            valor_total=valor_total,
            itens=itens_processados,
        )
        pedido = self.repo.criar(pedido)

        # ── 6. Log do pedido criado ───────────────────────────────────────────
        self.log.registrar(
            entidade_tipo="pedido",
            entidade_id=pedido.id,
            acao="criado",
            detalhes={
                "total_itens": len(itens_processados),
                "valor_total": str(valor_total),
            },
        )

        # ── 7. Commit — só aqui a transação fecha ────────────────────────────
        # Se qualquer etapa acima tiver falhado, uma exceção já foi lançada
        # e o SQLAlchemy faz rollback automático — o banco fica limpo
        self.db.commit()
        self.db.refresh(pedido)
        return OrderResponse.model_validate(pedido)

    def buscar_por_id(self, pedido_id: UUID) -> OrderResponse:
        """Busca com 404 claro se não encontrar."""
        pedido = self.repo.buscar_por_id(pedido_id)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pedido '{pedido_id}' não encontrado",
            )
        return OrderResponse.model_validate(pedido)

    def listar(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> PaginatedResponse[OrderResponse]:
        """Listagem paginada de pedidos."""
        pedidos, total = self.repo.listar(skip=skip, limit=limit)
        return PaginatedResponse(
            items=[OrderResponse.model_validate(p) for p in pedidos],
            total_count=total,
            skip=skip,
            limit=limit,
        )

    def cancelar(self, pedido_id: UUID) -> OrderResponse:
        """
        Cancelamento com estorno de estoque.

        Fluxo inverso da criação:
          1. Verifico se o pedido existe
          2. Verifico se já não foi cancelado — não cancelo duas vezes
          3. Estorno o estoque de cada item
          4. Atualizo o status para 'cancelado'
          5. Registro o log
          6. Commit

        Tudo na mesma transação — se o estorno de algum item falhar,
        o status do pedido não muda.
        """
        pedido = self.repo.buscar_por_id(pedido_id)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pedido '{pedido_id}' não encontrado",
            )

        # Não cancelo o que já foi cancelado — idempotência explícita
        if pedido.status == "cancelado":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pedido já foi cancelado",
            )

        # ── Estorno de estoque por item ───────────────────────────────────────
        for item in pedido.itens:
            self.produto_repo.incrementar_estoque(item.produto_id, item.quantidade)

            self.log.registrar(
                entidade_tipo="produto",
                entidade_id=item.produto_id,
                acao="estoque_estornado",
                detalhes={
                    "quantidade_estornada": item.quantidade,
                    "motivo": "cancelamento_pedido",
                    "pedido_id": str(pedido_id),
                },
            )

        # ── Atualizo o status ─────────────────────────────────────────────────
        pedido_cancelado = self.repo.atualizar_status(pedido_id, "cancelado")

        self.log.registrar(
            entidade_tipo="pedido",
            entidade_id=pedido_id,
            acao="cancelado",
            detalhes={"total_itens_estornados": len(pedido.itens)},
        )

        self.db.commit()
        self.db.refresh(pedido_cancelado)
        return OrderResponse.model_validate(pedido_cancelado)

    def obter_dashboard_dados(self) -> dict:
        """Dados de pedido para o dashboard."""
        return {
            "pedidos_hoje": self.repo.contar_pedidos_hoje(),
        }