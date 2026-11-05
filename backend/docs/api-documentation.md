# API quick reference

Swagger UI and OpenAPI are served at `/docs` and `/openapi.json` in development.

## Existing frontend requests

`POST /api/v1/contact`

```json
{
  "name": "Alex Customer",
  "email": "alex@example.com",
  "phone": "(503) 555-1234",
  "program": "Personal Training",
  "goals": "Build a steady strength routine",
  "preferredContact": "Email",
  "message": "Please get in touch."
}
```

Returns `{ "id": "<uuid>", "message": "..." }`, as expected by the current Next.js contact form.

`POST /api/v1/bookings` accepts `name`, `email`, `phone`, `program`, `date` (`YYYY-MM-DD`), `time` (ISO or `9:00 AM`), `goals`, and optional `notes`. It creates a `PENDING` consultation request, never a confirmed appointment. `Idempotency-Key` is accepted for retry-safe submission.

Public content: `GET /programs`, `GET /programs/{slug}`, `GET /program-categories`, `GET /trainers`, `GET /trainers/{slug}`, `GET /testimonials`, `GET /blog`, `GET /blog/{slug}`, `GET /blog/categories`, `GET /locations`.

Protected administrative APIs are under `/api/v1/admin/`; authenticate with `Authorization: Bearer <access_token>`. Login is `POST /api/v1/auth/login`; refresh rotates the opaque refresh token using `POST /api/v1/auth/refresh`.

Validation errors return a message and field-to-messages mapping. Public content list APIs return plain arrays and form submissions return the existing frontend's simple `{id, message}` shape.
