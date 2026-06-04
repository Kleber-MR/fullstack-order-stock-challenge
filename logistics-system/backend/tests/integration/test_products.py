"""
tests/integration/test_products.py

Testa todos os endpoints de produto.
Cobre a Fase 1 (CRUD) e Fase 2 (validações e erros) do teste técnico.
"""

import pytest


# ─── POST /api/v1/products ────────────────────────────────────────────────────

class TestCriarProduto:

    def test_cria_produto_com_sucesso(self, client):
        """Fluxo feliz — produto válido retorna 201 com os dados."""
        res = client.post("/api/v1/products", json={
            "nome": "Camiseta Básica",
            "sku": "CAM-001",
            "preco": 49.90,
            "quantidade_estoque": 100,
        })
        assert res.status_code == 201
        data = res.json()
        assert data["sku"] == "CAM-001"
        assert data["quantidade_estoque"] == 100
        assert "id" in data
        assert "data_criacao" in data

    def test_sku_normalizado_para_maiusculo(self, client):
        """SKU sempre salvo em maiúsculo — independente do que veio."""
        res = client.post("/api/v1/products", json={
            "nome": "Produto",
            "sku": "cam-001",
            "preco": 10.00,
            "quantidade_estoque": 5,
        })
        assert res.status_code == 201
        assert res.json()["sku"] == "CAM-001"

    def test_sku_duplicado_retorna_409(self, client, produto_base):
        """SKU já existente deve retornar 409 Conflict."""
        res = client.post("/api/v1/products", json={
            "nome": "Outro Produto",
            "sku": produto_base["sku"],
            "preco": 20.00,
            "quantidade_estoque": 5,
        })
        assert res.status_code == 409

    def test_preco_zero_retorna_422(self, client):
        """Preço zero deve ser rejeitado na validação."""
        res = client.post("/api/v1/products", json={
            "nome": "Produto",
            "sku": "PROD-X",
            "preco": 0,
            "quantidade_estoque": 5,
        })
        assert res.status_code == 422

    def test_preco_negativo_retorna_422(self, client):
        """Preço negativo deve ser rejeitado na validação."""
        res = client.post("/api/v1/products", json={
            "nome": "Produto",
            "sku": "PROD-X",
            "preco": -10,
            "quantidade_estoque": 5,
        })
        assert res.status_code == 422

    def test_estoque_negativo_retorna_422(self, client):
        """Estoque negativo deve ser rejeitado na validação."""
        res = client.post("/api/v1/products", json={
            "nome": "Produto",
            "sku": "PROD-X",
            "preco": 10.00,
            "quantidade_estoque": -1,
        })
        assert res.status_code == 422

    def test_sku_com_caractere_especial_retorna_422(self, client):
        """SKU com caracteres inválidos deve ser rejeitado."""
        res = client.post("/api/v1/products", json={
            "nome": "Produto",
            "sku": "PROD @#$",
            "preco": 10.00,
            "quantidade_estoque": 5,
        })
        assert res.status_code == 422

    def test_nome_vazio_retorna_422(self, client):
        """Nome vazio deve ser rejeitado."""
        res = client.post("/api/v1/products", json={
            "nome": "",
            "sku": "PROD-001",
            "preco": 10.00,
            "quantidade_estoque": 5,
        })
        assert res.status_code == 422


# ─── GET /api/v1/products ─────────────────────────────────────────────────────

class TestListarProdutos:

    def test_lista_vazia_retorna_200(self, client):
        """Lista vazia ainda é 200 — não é 404."""
        res = client.get("/api/v1/products")
        assert res.status_code == 200
        data = res.json()
        assert data["items"] == []
        assert data["total_count"] == 0

    def test_lista_com_produto(self, client, produto_base):
        """Produto criado aparece na listagem."""
        res = client.get("/api/v1/products")
        assert res.status_code == 200
        assert res.json()["total_count"] == 1

    def test_filtro_por_search(self, client, produto_base):
        """Filtro de busca por nome retorna apenas o produto correto."""
        res = client.get("/api/v1/products", params={"search": "Produto"})
        assert res.status_code == 200
        assert res.json()["total_count"] == 1

        res = client.get("/api/v1/products", params={"search": "inexistente"})
        assert res.json()["total_count"] == 0

    def test_filtro_in_stock(self, client, produto_base, produto_sem_estoque):
        """Filtro in_stock=true retorna só produtos com estoque."""
        res = client.get("/api/v1/products", params={"in_stock": True})
        assert res.status_code == 200
        assert res.json()["total_count"] == 1

    def test_paginacao(self, client, client_com_dois_produtos):
        """skip e limit funcionam corretamente."""
        res = client.get("/api/v1/products", params={"skip": 0, "limit": 1})
        assert len(res.json()["items"]) == 1
        assert res.json()["total_count"] == 2


# ─── GET /api/v1/products/{id} ────────────────────────────────────────────────

class TestBuscarProduto:

    def test_busca_produto_existente(self, client, produto_base):
        """Produto existente retorna 200."""
        res = client.get(f"/api/v1/products/{produto_base['id']}")
        assert res.status_code == 200
        assert res.json()["id"] == produto_base["id"]

    def test_produto_inexistente_retorna_404(self, client):
        """ID que não existe deve retornar 404."""
        res = client.get("/api/v1/products/99999")
        assert res.status_code == 404


# ─── PATCH /api/v1/products/{id} ─────────────────────────────────────────────

class TestAtualizarProduto:

    def test_atualiza_nome(self, client, produto_base):
        """Atualização parcial de nome funciona."""
        res = client.patch(
            f"/api/v1/products/{produto_base['id']}",
            json={"nome": "Novo Nome"},
        )
        assert res.status_code == 200
        assert res.json()["nome"] == "Novo Nome"

    def test_patch_vazio_retorna_422(self, client, produto_base):
        """PATCH sem campos deve ser rejeitado."""
        res = client.patch(
            f"/api/v1/products/{produto_base['id']}",
            json={},
        )
        assert res.status_code == 422

    def test_produto_inexistente_retorna_404(self, client):
        """PATCH com nome válido em produto inexistente retorna 404."""
        # Nome com pelo menos 2 caracteres para passar na validação do schema
        res = client.patch("/api/v1/products/99999", json={"nome": "Nome Valido"})
        assert res.status_code == 404


# ─── GET /api/v1/products/low-stock ──────────────────────────────────────────

class TestEstoqueBaixo:

    def test_retorna_produtos_abaixo_threshold(self, client, produto_sem_estoque):
        """Produto com estoque zero aparece no alerta."""
        res = client.get("/api/v1/products/low-stock", params={"threshold": 5})
        assert res.status_code == 200
        assert len(res.json()) >= 1

    def test_retorna_vazio_quando_todos_ok(self, client, produto_base):
        """Produto com estoque 10 não aparece com threshold 5."""
        res = client.get("/api/v1/products/low-stock", params={"threshold": 5})
        assert res.status_code == 200
        assert len(res.json()) == 0


# ─── Fixture auxiliar ─────────────────────────────────────────────────────────

@pytest.fixture
def client_com_dois_produtos(client):
    """Cria dois produtos para testar paginação."""
    client.post("/api/v1/products", json={
        "nome": "Produto A", "sku": "PROD-A", "preco": 10.00, "quantidade_estoque": 5
    })
    client.post("/api/v1/products", json={
        "nome": "Produto B", "sku": "PROD-B", "preco": 20.00, "quantidade_estoque": 5
    })
    return client