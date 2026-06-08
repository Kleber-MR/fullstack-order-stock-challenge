# Logistics Management System

API backend e dashboard frontend para gerenciamento de produtos, pedidos e estoque. Desenvolvido como parte de um desafio técnico fullstack com foco em clareza arquitetural, rastreabilidade de operações e confiabilidade transacional.

---

## Sumário

- [Visão geral](#visão-geral)
- [Decisões técnicas](#decisões-técnicas)
- [Arquitetura](#arquitetura)
- [Pré-requisitos](#pré-requisitos)
- [Como executar](#como-executar)
- [Endpoints](#endpoints)
- [Exemplos de uso](#exemplos-de-uso)
- [Regras de negócio](#regras-de-negócio)
- [Testes](#testes)
- [Estrutura do projeto](#estrutura-do-projeto)

---

## Visão geral

A aplicação permite cadastrar produtos com controle de estoque, criar pedidos com múltiplos itens e acompanhar o histórico de operações via logs de auditoria. Toda operação de escrita gera um log automático, e o cancelamento de pedidos realiza o estorno de estoque de forma atômica.

---

## Decisões técnicas

### Por que FastAPI?

FastAPI foi escolhido por gerar documentação OpenAPI automaticamente (Swagger + ReDoc), suportar validação via Pydantic v2 nativa e ter performance superior a frameworks síncronos. A tipagem estática em todo o projeto elimina uma classe inteira de erros em tempo de execução.

### Por que SQLAlchemy + Alembic?

O SQLAlchemy oferece ORM expressivo com suporte a operações atômicas como `UPDATE ... WHERE ... RETURNING`, essencial para o decremento seguro de estoque. O Alembic controla as migrations de forma versionada — nenhuma alteração no banco é feita manualmente.

### Por que PostgreSQL?

O modelo de dados envolve relações entre entidades com regras de unicidade e consistência transacional. O PostgreSQL garante integridade referencial via chaves estrangeiras, suporta `RETURNING` em updates atômicos e é o banco mais adequado para o padrão de queries do sistema.

### Por que Docker Compose?

Permite subir a aplicação completa — API e banco de dados — com um único comando, sem instalar dependências locais além do Docker. Garante paridade entre ambientes de desenvolvimento e produção.

### Atomicidade no decremento de estoque

O `UPDATE produtos SET estoque = estoque - N WHERE id = X AND estoque >= N` é executado em uma única operação no banco. Se dois pedidos simultâneos chegarem, o banco resolve sem race condition. Se o `RETURNING` retornar `None`, o service sabe que o estoque era insuficiente e faz rollback de toda a transação.

### Auditoria automática

Todo service que modifica dados chama o `LogService` dentro da mesma transação. Se a operação falhar, o log some junto — nunca há log de uma operação que não aconteceu.

---

## Arquitetura

```
backend/app/
├── core/
│   ├── database.py        # Engine, sessão, health check
│   └── settings.py        # Configurações via pydantic-settings
├── models/
│   ├── product.py         # Product
│   ├── order.py           # Order, OrderItem, OrderStatus
│   └── log.py             # Log, LogAction
├── schemas/
│   ├── common.py          # BaseResponse, PaginatedResponse, DashboardResponse
│   ├── product.py         # ProductCreate, ProductUpdate, ProductResponse
│   ├── order.py           # OrderCreate, OrderResponse, ItemPedidoResponse
│   └── log.py             # LogResponse
├── repositories/
│   ├── product_repository.py   # Queries de produto
│   ├── order_repository.py     # Queries de pedido
│   └── log_repository.py       # Inserção e leitura de logs
├── services/
│   ├── product_service.py      # Regras de negócio de produto
│   ├── order_service.py        # Regras de negócio de pedido (atomicidade)
│   ├── log_service.py          # Geração de logs de auditoria
│   └── dashboard_service.py    # Agregação de dados para o dashboard
├── routers/
│   ├── product_router.py
│   ├── order_router.py
│   ├── log_router.py
│   └── dashboard_router.py
└── main.py                # FastAPI, CORS, exception handlers, startup
```

```
frontend/src/
├── types/index.ts          # Interfaces TypeScript do domínio
├── services/
│   ├── api.ts              # Axios com interceptor de erro
│   ├── productService.ts
│   ├── orderService.ts
│   └── dashboardService.ts
├── pages/
│   ├── DashboardPage.tsx
│   ├── ProductListPage.tsx
│   ├── ProductCreatePage.tsx
│   ├── OrderListPage.tsx
│   ├── OrderCreatePage.tsx
│   └── LogPage.tsx
└── App.tsx                 # Sidebar, header, rotas
```

---

## Pré-requisitos

- Python 3.12+
- Node.js 18+
- Docker e Docker Compose

---

## Como executar

### Opção 1 — Docker Compose (recomendado)

```bash
docker-compose up --build
```

A API estará disponível em `http://localhost:8000` e o frontend em `http://localhost:5173`.

Para parar:

```bash
docker-compose down
```

Para parar e remover os dados do banco:

```bash
docker-compose down -v
```

### Opção 2 — Execução local

**Backend:**

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

pip install -r requirements.txt

# Configure o .env (copie o .env.example e preencha)
cp .env.example .env

# Suba o banco via Docker
docker-compose up db -d

# Execute as migrations
alembic upgrade head

# Inicie a API
uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

---

## Endpoints

| Método  | Rota                         | Descrição                             |
| ------- | ---------------------------- | ------------------------------------- |
| `GET`   | `/health`                    | Status da API e do banco              |
| `POST`  | `/api/v1/products`           | Criar produto                         |
| `GET`   | `/api/v1/products`           | Listar produtos (filtros + paginação) |
| `GET`   | `/api/v1/products/low-stock` | Produtos com estoque baixo            |
| `GET`   | `/api/v1/products/{id}`      | Buscar produto por ID                 |
| `PATCH` | `/api/v1/products/{id}`      | Atualizar produto parcialmente        |
| `POST`  | `/api/v1/orders`             | Criar pedido (decrementa estoque)     |
| `GET`   | `/api/v1/orders`             | Listar pedidos                        |
| `GET`   | `/api/v1/orders/{id}`        | Buscar pedido por ID                  |
| `PATCH` | `/api/v1/orders/{id}/cancel` | Cancelar pedido (estorna estoque)     |
| `GET`   | `/api/v1/logs`               | Logs de auditoria                     |
| `GET`   | `/api/v1/dashboard`          | Resumo do sistema                     |

Documentação interativa disponível em `http://localhost:8000/docs`.

---

## Exemplos de uso

### Criar produto

```bash
curl -X POST http://localhost:8000/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Camiseta Básica Preta",
    "sku": "CAM-001-P",
    "preco": 49.90,
    "quantidade_estoque": 100
  }'
```

### Criar pedido

```bash
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{
    "itens": [
      { "produto_id": 1, "quantidade": 3 }
    ]
  }'
```

### Cancelar pedido

```bash
curl -X PATCH http://localhost:8000/api/v1/orders/1/cancel
```

---

## Regras de negócio

| Cenário                               | Comportamento                               |
| ------------------------------------- | ------------------------------------------- |
| Criar produto com SKU duplicado       | `409 Conflict`                              |
| Criar produto com preço ≤ 0           | `422 Unprocessable Entity`                  |
| Criar pedido com produto inexistente  | `404 Not Found`                             |
| Criar pedido sem itens                | `422 Unprocessable Entity`                  |
| Criar pedido com produto duplicado    | `422 Unprocessable Entity`                  |
| Criar pedido com estoque insuficiente | `400 Bad Request` — nenhum estoque alterado |
| Cancelar pedido já cancelado          | `400 Bad Request`                           |
| Cancelar pedido existente             | Estoque de cada item estornado atomicamente |
| Qualquer operação de escrita          | Log de auditoria gerado automaticamente     |

---

## Testes

```bash
cd backend
pytest -v
```

```bash
cd backend
pytest --tb=short -q   # saída compacta
```

**Resultado atual:**

```
32 passed, 1 skipped in 1.92s
```

O teste pulado (`test_atomicidade_segundo_item_sem_estoque`) usa `UPDATE ... RETURNING`, sintaxe exclusiva do PostgreSQL — passa no banco real, incompatível com SQLite em memória usado nos testes.

**Cobertura dos módulos:**

| Módulo          | O que testa                                                             |
| --------------- | ----------------------------------------------------------------------- |
| `test_products` | CRUD completo, validações de SKU, preço, estoque, paginação, filtros    |
| `test_orders`   | Criação, estoque, atomicidade, snapshot de preço, cancelamento, estorno |

---

## Estrutura do projeto

```
logistics-system/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── repositories/
│   │   ├── services/
│   │   ├── routers/
│   │   └── main.py
│   ├── alembic/
│   ├── tests/
│   │   └── integration/
│   │       ├── test_products.py
│   │       └── test_orders.py
│   ├── .env.example
│   ├── alembic.ini
│   ├── pytest.ini
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── services/
│   │   └── types/
│   ├── .env.example
│   └── vite.config.ts
└── docker-compose.yml
```
