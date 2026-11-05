# Database schema

Business records use UUID primary keys and timezone-aware timestamps. PostgreSQL foreign keys and check constraints guard relations and allowed statuses.

- `users`, `roles`, `user_roles`, `refresh_tokens`: administrative identity and refresh-token rotation/revocation.
- `programs`, `trainers`: public content; inactive rows are hidden from public listings.
- `bookings`, `booking_status_history`: consultation requests, status transitions, and optional trainer assignment.
- `contact_enquiries`: lead records; email is indexed but deliberately not unique.
- `testimonials`: only rows explicitly marked published are public.
- `blog_categories`, `blog_posts`: draft/published articles.
- `locations`: opening hours remain nullable until the business confirms them.
- `notifications`: delivery state storage.
- `event_outbox`: durable business event delivery queue.
- `marketing_events`: campaign/source funnel tracking without required personal data.
- `processed_events`: unique `(event_id, handler)` marker for at-least-once consumers.

The idempotent seed script creates the provided business location, five program entries, and blog category labels. It does not seed staff, customer reviews, bookings, opening hours, or prices.
