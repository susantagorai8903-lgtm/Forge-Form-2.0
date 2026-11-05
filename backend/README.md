# Forge & Form Backend

Asynchronous modular-monolith backend for the Forge & Form Next.js site. The initial API contract keeps the existing frontend's public form field names and plain-array content responses.

## Architecture

- FastAPI and Pydantic v2 REST endpoints under `/api/v1`.
- SQLAlchemy 2 async sessions backed by PostgreSQL/Neon.
- Alembic-only schema changes; application startup never calls `create_all`.
- Argon2 password hashes, JWT access tokens, rotating opaque refresh tokens, and database-backed role assignments.
- Domain writes and corresponding Kafka events share a PostgreSQL transaction through `event_outbox`.
- Separate outbox publisher and notification consumer workers.

Review [architecture](docs/architecture.md), [schema](docs/database-schema.md), [API](docs/api-documentation.md), and [Kafka events](docs/kafka-events.md).

## Requirements and local setup

Use Python 3.12 or newer and Docker Compose. Compose provides PostgreSQL and Redpanda, so a local PostgreSQL installation is not needed. Stop any local service using port 5432 before starting Compose. From this directory:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
docker compose up -d postgres redpanda
python -m alembic upgrade head
python -m scripts.seed_data
docker compose up --build -d
```

The Compose API and workers start only after migrations and seeding are complete. The API listens on port 8000, PostgreSQL on 5432, and Redpanda's external Kafka listener on 19092. Swagger UI is at `http://localhost:8000/docs`. Do not also run host `uvicorn`; the Compose API already publishes port 8000.

Use `docker compose logs -f api` or `docker compose logs -f worker`. The outbox publisher is the `worker` service; the email consumer is `notification-worker`. `docker compose down` stops containers but preserves named data volumes.

## Configuration and database

Copy `.env.example` to `.env`. Never commit `.env` or live Kubernetes secrets. Set `DATABASE_URL` to a Neon `postgresql+asyncpg://` URL. Production requires a unique JWT secret and exact CORS origins; production database connections use SSL and a small pool suitable for serverless PostgreSQL.

Create and review migrations before deployment:

```powershell
python -m alembic revision --autogenerate -m "describe_change"
python -m alembic upgrade head
python -m alembic downgrade -1
```

The initial migration is checked into `alembic/versions/`. Test migrations against a disposable database; never use production data for integration tests. See [migration and deployment guidance](docs/deployment-guide.md).

## Authentication and authorization

- `POST /api/v1/auth/login` issues a short-lived access JWT and a random refresh token.
- `POST /api/v1/auth/refresh` rotates and revokes the prior refresh token.
- `POST /api/v1/auth/logout` revokes a refresh token.
- `GET /api/v1/auth/me` returns the current account and roles.

Create the first administrator with `python -m scripts.create_admin`; it prompts for credentials and hashes the password with Argon2. Public registration is not available. Admin routes require `STAFF`, `ADMIN`, or `SUPER_ADMIN` (permissions can be narrowed as the administration UI evolves).

## API and frontend

The Next.js forms send the exact `name`, `email`, `phone`, `program`, `date`, `time`, `goals`, and related contact fields documented in [frontend integration](docs/frontend-integration.md). Set the frontend's `NEXT_PUBLIC_API_BASE_URL` to the backend origin and configure backend `CORS_ORIGINS`.

Consultation submissions are requests with `PENDING` status, not confirmed bookings. Opening hours and capacity remain unconfigured by default; `BOOKING_CAPACITY_PER_SLOT` may be configured by the business. Public content APIs expose active programs/trainers, published testimonials/articles, and active locations. The existing frontend currently renders local content data rather than calling its content services.

## Kafka and notifications

Business events are persisted before commit and published asynchronously from the outbox. Publishers claim rows using `FOR UPDATE SKIP LOCKED`; delivery is at least once. Notification events are consumed with manual offset commits, duplicate event markers, bounded retries, and a dead-letter topic. See [event envelopes and topics](docs/kafka-events.md). Kafka credentials and provider keys belong in the deployment secret store.

`EMAIL_PROVIDER=console` is safe for local development and does not send mail. `EMAIL_PROVIDER=resend` requires a Resend API key and verified sender address. The notification worker sends customer request acknowledgements and internal business alerts; booking status messages reflect the actual persisted transition.

Outbox rows that exceed retry attempts remain `FAILED`; inspect them and run `python -m scripts.replay_outbox <event-id>` to requeue one. Consumer dead-letter messages require operator inspection and a deliberate replay procedure.

## Tests and checks

```powershell
python -m pytest
python -m alembic check
```

Tests use isolated in-memory SQLite and never connect to Neon. They cover frontend form contracts, outbox persistence, booking idempotency/past-date validation, duplicate enquiries, admin protection, and notification consumer deduplication. `alembic check` requires a reachable configured database; use a disposable PostgreSQL instance to verify production-dialect migration behavior.

## Deployment

- Render web service and workers: review root `render.yaml` and configure its secret variables.
- Kubernetes: review `k8s/`; create Secrets out-of-band and point the deployments at managed Neon and Kafka.
- Docker: `docker/Dockerfile` is shared by the API and worker processes.

See [deployment guide](docs/deployment-guide.md). Do not deploy the example Secret manifest or use its placeholder values.

## Security and known scope

The app validates bounded input, uses ORM-bound parameters, returns safe error messages, applies CORS and per-process public/login throttling, and avoids logging request bodies or tokens. For multi-replica production, enforce shared rate limits and request-body limits at the ingress/WAF. Configure HTTPS and secret rotation at the platform.

Analytics endpoints currently aggregate persisted bookings, enquiries, and marketing-event records directly. Separate analytics projection/booking consumers, Prometheus business/Kafka metrics, password reset/MFA, and a customer portal are not implemented. Do not treat aggregate enquiry-to-booking ratios as person-level attribution or report paid memberships; no payment/membership feature exists.
