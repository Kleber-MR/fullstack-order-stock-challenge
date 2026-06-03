"""
ProductService — regras de negócio de produto.

Aqui ficam as decisões de negócio — o repository só executa queries,
o service decide O QUE fazer e QUANDO fazer.

Responsabilidades:
  - Validar unicidade de SKU antes de criar
  - Garantir que estoque nunca fique negativo
  - Registrar log em toda operação que modifica dados
  - Controlar a transação — commit só acontece quando tudo deu certo
"""

from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.product import Produto
from app.repositories.product_repository import ProductRepository
from app.schemas.common import DashboardResponse, PaginatedResponse
from app.schemas.product import (
    ProductCreate,
    ProductLowStockResponse,
    ProductResponse,
    ProductUpdate,
)
from app.services.log_service import LogService


class ProductService:

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ProductRepository(db)
        self.log = LogService(db)  # injeto o LogService — todo service tem acesso a ele

    def criar(self, dados: ProductCreate) -> ProductResponse:
        """
        Crio produto validando unicidade do SKU antes de qualquer INSERT.
        Se o SKU já existe lanço 409 — conflito de recurso.
        Registro o log dentro da mesma transação — se o INSERT falhar, o log some junto.
        """
        # Verifico unicidade antes de tentar inserir — erro claro antes de bater no banco
        produto_existente = self.repo.buscar_por_sku(dados.sku)
        if produto_existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Já existe um produto com o SKU '{dados.sku}'",
            )

        produto = Produto(
            nome=dados.nome,
            sku=dados.sku,
            preco=dados.preco,
            quantidade_estoque=dados.quantidade_estoque,
        )

        produto = self.repo.criar(produto)

        # Log dentro da mesma transação — atomicidade garantida
        self.log.registrar(
            entidade_tipo="produto",
            entidade_id=produto.id,
            acao="criado",
            detalhes={"sku": produto.sku, "preco": str(produto.preco)},
        )

        self.db.commit()
        self.db.refresh(produto)
        return ProductResponse.model_validate(produto)

    def buscar_por_id(self, produto_id: UUID) -> ProductResponse:
        """
        Busca por ID com 404 claro se não encontrar.
        Leitura não gera log — só operações que modificam dados.
        """
        produto = self.repo.buscar_por_id(produto_id)
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produto '{produto_id}' não encontrado",
            )
        return ProductResponse.model_validate(produto)

    def listar(
        self,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        in_stock: bool | None = None,
    ) -> PaginatedResponse[ProductResponse]:
        """
        Listagem com filtros compostos.
        Devolvo o PaginatedResponse já montado — o router não precisa saber de paginação.
        """
        produtos, total = self.repo.listar(
            skip=skip,
            limit=limit,
            search=search,
            min_price=min_price,
            max_price=max_price,
            in_stock=in_stock,
        )
        return PaginatedResponse(
            items=[ProductResponse.model_validate(p) for p in produtos],
            total_count=total,
            skip=skip,
            limit=limit,
        )

    def atualizar(self, produto_id: UUID, dados: ProductUpdate) -> ProductResponse:
        """
        Atualização parcial — só processo os campos que vieram preenchidos.
        Registro o que mudou no log para rastreabilidade completa.
        """
        # Verifico se o produto existe antes de tentar atualizar
        produto_atual = self.repo.buscar_por_id(produto_id)
        if not produto_atual:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produto '{produto_id}' não encontrado",
            )

        # Monto o dict só com os campos que realmente vieram — evito sobrescrever com None
        campos = dados.model_dump(exclude_none=True)

        produto_atualizado = self.repo.atualizar(produto_id, campos)

        self.log.registrar(
            entidade_tipo="produto",
            entidade_id=produto_id,
            acao="atualizado",
            detalhes={"campos_alterados": campos},
        )

        self.db.commit()
        self.db.refresh(produto_atualizado)
        return ProductResponse.model_validate(produto_atualizado)

    def listar_estoque_baixo(self, threshold: int = 10) -> list[ProductLowStockResponse]:
        """
        Alerta de estoque baixo com threshold configurável.
        O threshold vem do endpoint — flexível para diferentes contextos.
        """
        if threshold < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Threshold não pode ser negativo",
            )

        produtos = self.repo.listar_estoque_baixo(threshold)
        return [
            ProductLowStockResponse(
                id=p.id,
                nome=p.nome,
                sku=p.sku,
                quantidade_estoque=p.quantidade_estoque,
                threshold=threshold,  # devolvo o threshold usado — útil pro frontend
            )
            for p in produtos
        ]

    def obter_dashboard_dados(self) -> dict:
        """
        Dados agregados para o dashboard — delego ao repository as queries pesadas.
        Devolvo dict porque o DashboardResponse é montado no service de dashboard
        junto com os dados de pedidos.
        """
        return {
            "total_produtos": len(self.repo.listar(limit=1)[0]),  # só o count
            "valor_total_estoque": self.repo.calcular_valor_total_estoque(),
            "itens_estoque_critico": self.repo.contar_estoque_critico(threshold=10),
        }