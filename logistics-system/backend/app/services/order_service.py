"""
OrderService — regras de negócio de pedido.

Esse é o service mais crítico do sistema.
Criação de pedido é uma operação atômica — ou tudo acontece ou nada acontece.

Fluxo de criação:
  1. Verifico se todos os produtos existem        ← Fase 1: só leitura
  2. Verifico se todos têm estoque suficiente     ← Fase 1: só leitura
  3. Decremento o estoque de cada item            ← Fase 2: escrita começa aqui
  4. Calculo o valor total com o preço atual
  5. Crio o pedido com os itens
  6. Registro o log
  7. Commit — só aqui a transação fecha

CORRIGIDO: separei validação e escrita em duas fases.
Se qualquer validação falhar, nenhuma escrita aconteceu — rollback limpo.
"""

from decimal import Decimal

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
        self.produto_repo = ProductRepository(db)
        self.log = LogService(db)

    def criar(self, dados: OrderCreate) -> OrderResponse:
        """
        Criação de pedido com atomicidade total.

        Por que duas fases?
        Na fase 1 só leio — se qualquer validação falhar, nada foi escrito.
        Na fase 2 só escrevo — todas as validações já passaram.
        Isso evita rollback parcial onde alguns estoques foram decrementados
        e outros não, deixando o banco em estado inconsistente.
        """

        # ── Fase 1: valida TUDO antes de escrever qualquer coisa ─────────────
        produtos_validados = []
        for item in dados.itens:
            produto = self.produto_repo.buscar_por_id(item.produto_id)

            if not produto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Produto '{item.produto_id}' não encontrado",
                )

            if produto.quantidade_estoque < item.quantidade:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Estoque insuficiente para '{produto.nome}'. "
                        f"Disponível: {produto.quantidade_estoque}, "
                        f"Solicitado: {item.quantidade}"
                    ),
                )

            produtos_validados.append((produto, item.quantidade))

        # ── Fase 2: escreve — todas as validações já passaram ────────────────
        itens_processados = []
        valor_total = Decimal("0")  # CORRIGIDO: Decimal desde o início, não int/float

        for produto, quantidade in produtos_validados:
            produto_atualizado = self.produto_repo.decrementar_estoque(
                produto.id, quantidade
            )
            if not produto_atualizado:
                # Proteção extra: race condition entre a validação e o decremento
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Estoque insuficiente para '{produto.nome}' — tente novamente",
                )

            preco_unitario = Decimal(str(produto.preco))
            subtotal = preco_unitario * quantidade
            valor_total += subtotal

            itens_processados.append(
                ItemPedido(
                    produto_id=produto.id,
                    quantidade=quantidade,
                    preco_unitario=preco_unitario,
                    subtotal=subtotal,
                )
            )

            self.log.registrar(
                entidade_tipo="produto",
                entidade_id=produto.id,
                acao="estoque_decrementado",
                detalhes={
                    "quantidade_decrementada": quantidade,
                    "estoque_restante": produto_atualizado.quantidade_estoque,
                    "motivo": "criacao_pedido",
                },
            )

        pedido = Pedido(
            status="pendente",
            valor_total=valor_total,
            itens=itens_processados,
        )
        pedido = self.repo.criar(pedido)

        self.log.registrar(
            entidade_tipo="pedido",
            entidade_id=pedido.id,
            acao="criado",
            detalhes={
                "total_itens": len(itens_processados),
                "valor_total": str(valor_total),
            },
        )

        self.db.commit()
        self.db.refresh(pedido)
        return OrderResponse.model_validate(pedido)

    def buscar_por_id(self, pedido_id: int) -> OrderResponse:
        pedido = self.repo.buscar_por_id(pedido_id)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pedido '{pedido_id}' não encontrado",
            )
        return OrderResponse.model_validate(pedido)

    def listar(self, skip: int = 0, limit: int = 20) -> PaginatedResponse[OrderResponse]:
        pedidos, total = self.repo.listar(skip=skip, limit=limit)
        return PaginatedResponse(
            items=[OrderResponse.model_validate(p) for p in pedidos],
            total_count=total,
            skip=skip,
            limit=limit,
        )

    def cancelar(self, pedido_id: int) -> OrderResponse:
        """
        Cancelamento com estorno de estoque.
        Tudo na mesma transação — se o estorno de algum item falhar,
        o status do pedido não muda.
        """
        pedido = self.repo.buscar_por_id(pedido_id)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pedido '{pedido_id}' não encontrado",
            )

        if pedido.status == "cancelado":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pedido já foi cancelado",
            )

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
        return {
            "pedidos_hoje": self.repo.contar_pedidos_hoje(),
        }