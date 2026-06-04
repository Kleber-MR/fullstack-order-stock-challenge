"""
ProductRepository — toda query de produto passa por aqui.

O service nunca escreve SQL — ele chama métodos com nomes de negócio.
Recebo a sessão como parâmetro (injeção de dependência).
Devolvo objetos do modelo ou None — nunca lanço HTTP exceptions aqui.
"""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import cast, Date, func, select, update
from sqlalchemy.orm import Session

from app.models.product import Produto


class ProductRepository:

    def __init__(self, db: Session) -> None:
        self.db = db

    def criar(self, produto: Produto) -> Produto:
        """
        Persisto o objeto e atualizo ele com os dados gerados pelo banco
        (id, data_criacao) sem precisar fazer uma segunda query.
        """
        self.db.add(produto)
        self.db.flush()
        self.db.refresh(produto)
        return produto

    def buscar_por_id(self, produto_id: int) -> Produto | None:
        return self.db.get(Produto, produto_id)

    def buscar_por_sku(self, sku: str) -> Produto | None:
        stmt = select(Produto).where(Produto.sku == sku.upper())
        return self.db.scalar(stmt)

    def listar(
        self,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        in_stock: bool | None = None,
    ) -> tuple[list[Produto], int]:
        """
        Listagem com filtros compostos e paginação.
        Devolvo a lista E o total — o frontend precisa dos dois para paginar.
        Construo a query dinamicamente só com os filtros que chegaram.
        """
        stmt = select(Produto)
        count_stmt = select(func.count()).select_from(Produto)

        if search:
            filtro = (
                Produto.nome.ilike(f"%{search}%") |
                Produto.sku.ilike(f"%{search}%")
            )
            stmt = stmt.where(filtro)
            count_stmt = count_stmt.where(filtro)

        if min_price is not None:
            stmt = stmt.where(Produto.preco >= min_price)
            count_stmt = count_stmt.where(Produto.preco >= min_price)

        if max_price is not None:
            stmt = stmt.where(Produto.preco <= max_price)
            count_stmt = count_stmt.where(Produto.preco <= max_price)

        if in_stock is True:
            stmt = stmt.where(Produto.quantidade_estoque > 0)
            count_stmt = count_stmt.where(Produto.quantidade_estoque > 0)
        elif in_stock is False:
            stmt = stmt.where(Produto.quantidade_estoque == 0)
            count_stmt = count_stmt.where(Produto.quantidade_estoque == 0)

        total = self.db.scalar(count_stmt) or 0
        produtos = self.db.scalars(
            stmt.order_by(Produto.data_criacao.desc()).offset(skip).limit(limit)
        ).all()

        return list(produtos), total

    def listar_estoque_baixo(self, threshold: int) -> list[Produto]:
        stmt = (
            select(Produto)
            .where(Produto.quantidade_estoque <= threshold)
            .order_by(Produto.quantidade_estoque.asc())
        )
        return list(self.db.scalars(stmt).all())

    def atualizar(self, produto_id: int, dados: dict) -> Produto | None:
        """
        CORRIGIDO: busca o objeto, aplica os campos e faz flush.
        returning() não atualiza o cache da sessão — setattr é mais seguro.
        """
        produto = self.db.get(Produto, produto_id)
        if not produto:
            return None
        for campo, valor in dados.items():
            setattr(produto, campo, valor)
        self.db.flush()
        self.db.refresh(produto)
        return produto

    def decrementar_estoque(self, produto_id: int, quantidade: int) -> Produto | None:
        """
        Operação atômica de decremento de estoque.
        O WHERE garante que só executa se tiver estoque suficiente.
        Se retornar None, o service sabe que o estoque era insuficiente.
        Isso evita race condition em pedidos simultâneos.
        """
        stmt = (
            update(Produto)
            .where(
                Produto.id == produto_id,
                Produto.quantidade_estoque >= quantidade,
            )
            .values(quantidade_estoque=Produto.quantidade_estoque - quantidade)
            .returning(Produto)
        )
        return self.db.scalar(stmt)

    def incrementar_estoque(self, produto_id: int, quantidade: int) -> Produto | None:
        stmt = (
            update(Produto)
            .where(Produto.id == produto_id)
            .values(quantidade_estoque=Produto.quantidade_estoque + quantidade)
            .returning(Produto)
        )
        return self.db.scalar(stmt)

    def calcular_valor_total_estoque(self) -> Decimal:
        stmt = select(func.sum(Produto.preco * Produto.quantidade_estoque))
        return self.db.scalar(stmt) or Decimal("0")

    def contar_estoque_critico(self, threshold: int = 10) -> int:
        stmt = select(func.count()).select_from(Produto).where(
            Produto.quantidade_estoque <= threshold
        )
        return self.db.scalar(stmt) or 0

    def contar_pedidos_hoje(self) -> int:
        """
        CORRIGIDO: usa UTC para não depender do timezone da máquina.
        cast(Date) garante compatibilidade com PostgreSQL.
        """
        hoje = datetime.now(timezone.utc).date()
        stmt = select(func.count()).select_from(Produto).where(
            cast(Produto.data_criacao, Date) == hoje
        )
        return self.db.scalar(stmt) or 0