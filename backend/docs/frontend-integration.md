# Frontend integration contract

The current Next.js API client uses `NEXT_PUBLIC_API_BASE_URL`, appends `/api/v1`, and sends:

- contact keys: `name`, `email`, `phone`, `program`, `goals`, `preferredContact`, `message`
- booking keys: `name`, `email`, `phone`, `program`, `date`, `time`, `goals`, `notes`

Set `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000` locally and configure the deployed frontend origin in backend `CORS_ORIGINS`. Backend form responses intentionally retain `{id, message}`. Program, trainer, testimonial, and article public JSON is mapped to the existing TypeScript content shapes. The frontend currently renders local content data and does not call its content service functions; connecting those pages to API content should be a separate deliberate frontend change.

Do not treat the sample booking times rendered in the frontend as confirmed studio hours. Booking submissions are requests in `PENDING` status.
