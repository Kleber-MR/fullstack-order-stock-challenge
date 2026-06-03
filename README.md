# Logistics System

Sistema de gerenciamento de pedidos e estoque.

## Stack

| Camada    | Tecnologia                           |
| --------- | ------------------------------------ |
| Backend   | Python 3.12 · FastAPI · SQLAlchemy 2 |
| Banco     | PostgreSQL 16                        |
| Migrações | Alembic                              |
| Frontend  | React 18 · TypeScript · Vite         |
| Container | Docker · Docker Compose              |

## Estrutura

```
logistics-system/
├── backend/      FastAPI + SQLAlchemy
├── frontend/     React + TypeScript
├── docs/         Decisões de arquitetura e contratos de API
└── docker-compose.yml
```

## Início rápido

```bash
# 1. Sobe o banco
docker-compose up db -d

# 2. Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# 3. Frontend (outro terminal)
cd frontend
npm install
npm run dev
```

Acesse:

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Frontend: http://localhost:5173
