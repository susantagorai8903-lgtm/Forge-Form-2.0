import time

import pytest
from sqlalchemy import func, select
from uuid import UUID
from zoneinfo import ZoneInfoNotFoundError

from app.main import app, request_counts
from app.models import ContactEnquiry, EventOutbox
from app.api.v1.endpoints import bookings


@pytest.mark.asyncio
async def test_contact_preserves_frontend_contract_and_outboxes_event(client):
    response = await client.post("/api/v1/contact", json={
        "name": "Alex Customer",
        "email": "alex@example.com",
        "phone": "(503) 555-1234",
        "program": "Personal Training",
        "goals": "Build a steady strength routine",
        "preferredContact": "Email",
        "message": "Please get in touch.",
    })
    assert response.status_code == 201
    assert set(response.json()) == {"id", "message"}
    assert response.json()["id"]
    assert response.headers["x-correlation-id"]
    async with app.state.test_sessions() as session:
        enquiry = await session.scalar(select(ContactEnquiry).where(ContactEnquiry.id == UUID(response.json()["id"])))
        assert enquiry is not None
        events = (await session.scalars(select(EventOutbox))).all()
        assert any(event.event_type == "forgeform.contact.created" for event in events)
        assert sum(event.event_type == "forgeform.notification.requested" for event in events) == 2


@pytest.mark.asyncio
async def test_booking_request_starts_pending_and_supports_idempotency(client):
    request = {
        "name": "Alex Customer",
        "email": "alex@example.com",
        "phone": "(503) 555-1234",
        "program": "Personal Training",
        "date": "2099-01-02",
        "time": "9:00 AM",
        "goals": "Build a steady strength routine",
        "notes": "",
    }
    headers = {"Idempotency-Key": "test-key-001"}
    first = await client.post("/api/v1/bookings", json=request, headers=headers)
    past_date_retry = await client.post(
        "/api/v1/bookings",
        json={**request, "date": "2000-01-02"},
        headers=headers,
    )
    unavailable_program_retry = await client.post(
        "/api/v1/bookings",
        json={**request, "program": "unavailable-program"},
        headers=headers,
    )
    assert first.status_code == 201
    assert past_date_retry.status_code == 201
    assert unavailable_program_retry.status_code == 201
    assert past_date_retry.json()["id"] == first.json()["id"]
    assert unavailable_program_retry.json()["id"] == first.json()["id"]


@pytest.mark.asyncio
async def test_invalid_email_is_rejected(client):
    response = await client.post("/api/v1/contact", json={
        "name": "Alex Customer",
        "email": "not-an-email",
        "phone": "(503) 555-1234",
        "program": "Personal Training",
        "goals": "Build a steady strength routine",
        "preferredContact": "Email",
        "message": "Please get in touch.",
    })
    assert response.status_code == 422
    assert response.json()["message"] == "Validation failed"


@pytest.mark.asyncio
async def test_booking_in_the_past_is_rejected(client):
    response = await client.post("/api/v1/bookings", json={
        "name": "Alex Customer",
        "email": "alex@example.com",
        "phone": "(503) 555-1234",
        "program": "Personal Training",
        "date": "2000-01-02",
        "time": "9:00 AM",
        "goals": "Build a steady strength routine",
    })
    assert response.status_code == 422
    assert response.json()["message"] == "Preferred date cannot be in the past"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "timezone_error",
    [ZoneInfoNotFoundError("unknown"), ValueError("invalid"), OSError("unavailable")],
)
async def test_invalid_timezone_errors_return_422(client, monkeypatch, timezone_error):
    def invalid_zone(_timezone_name):
        raise timezone_error

    monkeypatch.setattr(bookings, "ZoneInfo", invalid_zone)
    response = await client.post("/api/v1/bookings", json={
        "name": "Alex Customer",
        "email": "alex@example.com",
        "phone": "(503) 555-1234",
        "program": "Personal Training",
        "date": "2099-01-02",
        "time": "9:00 AM",
        "goals": "Build a steady strength routine",
        "timezone": "Invalid/Zone",
    })
    assert response.status_code == 422
    assert response.json()["message"] == "Invalid timezone"


@pytest.mark.asyncio
async def test_repeat_contact_enquiries_from_same_email_are_allowed(client):
    payload = {
        "name": "Alex Customer",
        "email": "alex@example.com",
        "phone": "(503) 555-1234",
        "program": "Personal Training",
        "goals": "Build a steady strength routine",
        "preferredContact": "Email",
        "message": "Please get in touch.",
    }
    first = await client.post("/api/v1/contact", json=payload)
    second = await client.post("/api/v1/contact", json=payload)
    assert first.status_code == second.status_code == 201
    async with app.state.test_sessions() as session:
        count = await session.scalar(select(func.count()).select_from(ContactEnquiry))
    assert count == 2


@pytest.mark.asyncio
async def test_admin_routes_require_authentication(client):
    response = await client.get("/api/v1/admin/analytics/overview")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_large_request_body_is_rejected(client):
    response = await client.post("/api/v1/contact", content=b"x" * 70000, headers={"content-type": "application/json"})
    assert response.status_code == 413


@pytest.mark.asyncio
async def test_login_is_rate_limited(client):
    results = []
    for _ in range(6):
        response = await client.post("/api/v1/auth/login", json={
            "email": "unknown@example.com",
            "password": "not-the-password",
        })
        results.append(response.status_code)
    assert results == [401, 401, 401, 401, 401, 429]


@pytest.mark.asyncio
async def test_unmatched_routes_and_unsupported_methods_use_http_error_envelope(client):
    not_found = await client.get("/not-found")
    unsupported_method = await client.get("/api/v1/contact")
    for response in (not_found, unsupported_method):
        assert set(response.json()) == {"success", "message", "errors", "meta"}
    assert not_found.status_code == 404
    assert unsupported_method.status_code == 405


@pytest.mark.asyncio
async def test_marketing_events_are_rate_limited_separately(client):
    payload = {"event_type": "PAGE_VIEW"}
    assert (await client.post("/api/v1/marketing-events", json=payload)).status_code == 202
    bucket = next(bucket for key, bucket in request_counts.items() if key.endswith("analytics"))
    bucket.extend([time.monotonic()] * 119)

    response = await client.post("/api/v1/marketing-events", json=payload)

    assert response.status_code == 429
