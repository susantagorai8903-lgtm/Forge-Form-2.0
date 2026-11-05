# Deployment

## Render

The root `render.yaml` defines an API web service and independent outbox worker. Review the blueprint, then configure the referenced secrets in Render.

Configure environment variables in Render's secret settings. Run `alembic upgrade head` as a release/pre-deploy command, then run `python -m scripts.seed_data` once. Create the first admin interactively using `python -m scripts.create_admin`; do not store its password in service environment.

## Neon

Set `DATABASE_URL` to the Neon connection string using `postgresql+asyncpg://`. Production mode configures SSL and a modest application pool. Use a separate database or branch for tests and migrations.

## Kubernetes

Review the example ConfigMap and Secret, then create the actual secret out-of-band (external secret manager or `kubectl create secret`). Replace the image placeholder, apply ConfigMap/Secret, Deployment, Service, and worker Deployment. Run migrations as a one-off deployment/job before rolling out application replicas. PostgreSQL and Kafka are external managed services.

## Local Compose

From `backend`, copy `.env.example` to `.env`, then run `docker compose up --build`; apply migrations in another terminal with `alembic upgrade head` and seed with `python -m scripts.seed_data`. Stop with `docker compose down`; volumes persist. Local-only credentials in Compose are not production credentials.
