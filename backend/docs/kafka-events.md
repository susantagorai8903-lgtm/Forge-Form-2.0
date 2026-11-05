# Kafka events

Event values are JSON envelopes: `event_id` (UUID), `event_type`, `event_version` (starts at 1), `occurred_at` (UTC ISO timestamp), `aggregate_id`, nullable `correlation_id`, `source`, and `payload`.

The outbox stores events before delivery. API domain events currently include booking created/confirmed/cancelled, contact created/updated, program/trainer updated, marketing analytics event. Each topic is defined centrally in `app/kafka/topics.py`.

| Topic | Producer event | Payload summary |
|---|---|---|
| `forgeform.booking.created` | booking request transaction | booking ID, selected program |
| `forgeform.booking.confirmed` | authorized status transition | booking ID and status |
| `forgeform.booking.cancelled` | cancellation or authorized transition | booking ID |
| `forgeform.booking.updated` | authorized completion/rejection transition | booking ID and status |
| `forgeform.contact.created` | contact submission | enquiry ID, program, source |
| `forgeform.contact.updated` | admin status change | enquiry ID, status |
| `forgeform.notification.requested` | reserved for notification delivery requests | notification ID and template data |
| `forgeform.notification.sent` | reserved for successful provider delivery | notification ID |
| `forgeform.notification.failed` | reserved for permanent provider failure | notification ID and failure code |
| `forgeform.analytics.event` | marketing event submission | event name, source, campaign, landing page |
| `forgeform.program.updated` | program create/update | program ID |
| `forgeform.trainer.updated` | trainer create/update | trainer ID |
| `forgeform.events.dlq` | exhausted notification consumer retries | original event envelope, event ID, failure class |

Use the event ID plus handler name as the idempotency key in consumer side effects. The outbox retries with bounded exponential backoff; after the configured attempt limit, it logs and retains the failed row. Operators can inspect it and run `python -m scripts.replay_outbox <event-id>` to requeue it. Never assume Kafka alone provides exactly-once business behavior.

The notification worker consumes `forgeform.notification.requested` with manual commits, records idempotency in `processed_events`, retries transient errors, and forwards permanently failing messages to `forgeform.events.dlq`. Resend API idempotency keys protect retry delivery. The current backend does not implement a separate booking projection or analytics projection consumer; analytics endpoints query persisted records directly.
