# Forge & Form Personal Training

The repository contains the Forge & Form Next.js frontend and a separate asynchronous FastAPI backend in [`backend/`](./backend/). Backend integration preserves the frontend's existing REST contracts for contact enquiries and consultation requests.

## Backend quick start

Prerequisites: Python 3.12+ and Docker Compose. Compose provides PostgreSQL and Redpanda; you do not need a local PostgreSQL installation. Stop any local service using port 5432 before starting Compose.

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
docker compose up -d postgres redpanda
python -m alembic upgrade head
python -m scripts.seed_data
```

After migrations and seeding, start the application using **one** of these options:

```powershell
# Option 1: run the API on the host
uvicorn app.main:app --reload
```

```powershell
# Option 2: run the API and workers with Compose (do not also run host Uvicorn)
docker compose up --build -d api worker notification-worker
```

The API docs are available at `http://localhost:8000/docs`. Stop local infrastructure with `docker compose down`; persistent local database and Kafka data remain in volumes.

To create the first administrator, run `python -m scripts.create_admin` from `backend`; the script prompts for credentials and does not create default accounts.

## Architecture and operations

- FastAPI + Pydantic v2 + async SQLAlchemy 2.
- Neon PostgreSQL with Alembic-managed migrations.
- JWT access tokens, rotating/revocable refresh tokens, Argon2 hashes, and role-based admin routes.
- PostgreSQL transactional outbox with a separate aiokafka publisher.
- Docker Compose local PostgreSQL/Redpanda and portable Kubernetes templates.
- API and deployment documentation: [`backend/docs/`](./backend/docs/).

Use `alembic revision --autogenerate -m "description"` to create reviewed migrations and `alembic upgrade head` to apply them. Never use ORM `create_all()` against deployed databases.

## Frontend connection

Set `NEXT_PUBLIC_API_BASE_URL` to the backend origin (for example `http://localhost:8000`) and set backend `CORS_ORIGINS` to the exact frontend origin. The contact and booking forms currently send their existing frontend field names. Full API contracts and known integration scope are in [`backend/docs/frontend-integration.md`](./backend/docs/frontend-integration.md).

## Current implementation boundaries

The API, durable outbox publisher, notification consumer, and configurable Resend delivery are implemented; live sending requires provider credentials. Analytics are database-backed, while dedicated analytics/booking projection consumers and Kafka/business-operation metrics remain out of scope. Public forms use per-process throttling; multi-replica deployments should also enforce shared limits at the ingress. The existing frontend uses local content datasets; its pages are not yet switched to remote content.