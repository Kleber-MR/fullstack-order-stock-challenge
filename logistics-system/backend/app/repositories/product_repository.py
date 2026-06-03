"""
ProductRepository — toda query de produto passa por aqui.

O service nunca escreve SQL — ele chama métodos com nomes de negócio.
Recebo a sessão como parâmetro (injeção de dependência).
Devolvo objetos do modelo ou None — nunca lanço HTTP exceptions aqui.
"""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.models.product import Produto


class ProductRepository:

    def __init__(self, db: Session) -> None:
        # Recebo a sessão pronta — não crio conexão aqui
        self.db = db

    def criar(self, produto: Produto) -> Produto:
        """
        Persisto o objeto e atualizo ele com os dados gerados pelo banco
        (id, data_criacao) sem precisar fazer uma segunda query.
        """
        self.db.add(produto)
        self.db.flush()          # executa o INSERT mas ainda não commita
        self.db.refresh(produto) # traz de volta os campos gerados pelo banco
        return produto

    def buscar_por_id(self, produto_id: UUID) -> Produto | None:
        """
        Busca simples por PK.
        Retorno None deixa o service decidir se isso é 404 ou fluxo alternativo.
        """
        return self.db.get(Produto, produto_id)

    def buscar_por_sku(self, sku: str) -> Produto | None:
        """
        Uso antes de criar produto para garantir unicidade do SKU.
        Se retornar algo, o service lança 409 Conflict.
        """
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

        # Aplico cada filtro só se ele foi passado — evito condições desnecessárias
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
        """
        Produtos abaixo do limite configurável.
        Threshold vem do endpoint — não hardcodo valor de negócio aqui.
        """
        stmt = (
            select(Produto)
            .where(Produto.quantidade_estoque <= threshold)
            .order_by(Produto.quantidade_estoque.asc())
        )
        return list(self.db.scalars(stmt).all())

    def atualizar(self, produto_id: UUID, dados: dict) -> Produto | None:
        """
        Atualização parcial com dicionário de campos.
        UPDATE direto — mais eficiente que buscar e modificar atributo a atributo.
        """
        stmt = (
            update(Produto)
            .where(Produto.id == produto_id)
            .values(**dados)
            .returning(Produto)
        )
        return self.db.scalar(stmt)

    def decrementar_estoque(self, produto_id: UUID, quantidade: int) -> Produto | None:
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
                Produto.quantidade_estoque >= quantidade,  # condição de guarda
            )
            .values(quantidade_estoque=Produto.quantidade_estoque - quantidade)
            .returning(Produto)
        )
        return self.db.scalar(stmt)

    def incrementar_estoque(self, produto_id: UUID, quantidade: int) -> Produto | None:
        """
        Estorno de estoque ao cancelar pedido.
        Operação inversa do decremento — também atômica.
        """
        stmt = (
            update(Produto)
            .where(Produto.id == produto_id)
            .values(quantidade_estoque=Produto.quantidade_estoque + quantidade)
            .returning(Produto)
        )
        return self.db.scalar(stmt)

    def calcular_valor_total_estoque(self) -> Decimal:
        """
        Soma preco * quantidade_estoque de todos os produtos.
        Faço no banco — não trago todos os produtos pra Python só pra somar.
        """
        stmt = select(func.sum(Produto.preco * Produto.quantidade_estoque))
        return self.db.scalar(stmt) or Decimal("0")

    def contar_estoque_critico(self, threshold: int = 10) -> int:
        """Conta produtos abaixo do threshold — usado no dashboard."""
        stmt = select(func.count()).select_from(Produto).where(
            Produto.quantidade_estoque <= threshold
        )
        return self.db.scalar(stmt) or 0