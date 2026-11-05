# Architecture

The backend is a modular FastAPI application using asynchronous SQLAlchemy sessions and PostgreSQL. API routes own request/response validation, SQLAlchemy models define the persistence boundary, and business events are recorded to `event_outbox` in the same transaction as the domain write.

The separate outbox worker claims rows with PostgreSQL `FOR UPDATE SKIP LOCKED`, publishes JSON to Kafka, and marks successful events published. Kafka delivery is at least once: a worker crash after publish but before commit can redeliver. Consumer handlers must deduplicate by `event_id`; Kafka idempotence does not make downstream business processing exactly once.

Do not run schema creation at application startup. Alembic is the production schema authority. The API does not require Kafka to accept a request; the outbox buffers events during Kafka outages.

## Deployment shape

- API: FastAPI on Render or Kubernetes.
- Database: managed Neon PostgreSQL.
- Outbox publisher: independent Render worker or Kubernetes Deployment.
- Kafka: managed Confluent/Redpanda or local Redpanda Compose.
- Email: provider configuration is reserved in settings; configure a verified sender before enabling delivery.
