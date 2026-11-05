import pytest

from app.core.security import hash_password
from app.core.config import settings
from app.main import app
from app.models import Location, Role, User


@pytest.mark.asyncio
async def test_admin_can_create_program_and_public_contract_is_preserved(client):
    async with app.state.test_sessions() as session:
        role = Role(name="ADMIN")
        user = User(
            full_name="Studio Admin",
            email="admin@example.com",
            password_hash=hash_password("Strong-test-password-2026"),
            is_active=True,
            is_verified=True,
        )
        user.roles.append(role)
        session.add(user)
        await session.commit()

    login = await client.post("/api/v1/auth/login", json={
        "email": "admin@example.com",
        "password": "Strong-test-password-2026",
    })
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    response = await client.post("/api/v1/admin/programs", headers=headers, json={
        "name": "Movement Coaching",
        "slug": "movement-coaching",
        "category": "Personal Training",
        "description": "A program description.",
        "short_description": "A concise summary.",
        "benefits": ["Coaching"],
        "target_audience": "People seeking coaching.",
        "image_url": "",
        "is_active": True,
        "display_order": 5,
    })
    assert response.status_code == 201
    assert response.json()["title"] == "Movement Coaching"
    assert response.json()["eyebrow"] == "Personal Training"


@pytest.mark.asyncio
async def test_public_programs_use_frontend_content_shape(client):
    response = await client.get("/api/v1/programs")
    assert response.status_code == 200
    program = response.json()[0]
    assert {
        "slug", "title", "eyebrow", "summary", "description", "image",
        "alt", "benefits", "suitableFor",
    }.issubset(program)


@pytest.mark.asyncio
async def test_booking_capacity_is_checked_when_admin_confirms(client, monkeypatch):
    monkeypatch.setattr(settings, "booking_capacity_per_slot", 1)
    async with app.state.test_sessions() as session:
        role = Role(name="ADMIN")
        user = User(
            full_name="Studio Admin",
            email="capacity-admin@example.com",
            password_hash=hash_password("Strong-test-password-2026"),
            is_active=True,
            is_verified=True,
        )
        user.roles.append(role)
        session.add(user)
        await session.commit()

    token = (await client.post("/api/v1/auth/login", json={
        "email": "capacity-admin@example.com",
        "password": "Strong-test-password-2026",
    })).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    request = {
        "name": "Alex Customer",
        "email": "alex@example.com",
        "phone": "(503) 555-1234",
        "program": "Personal Training",
        "date": "2099-01-02",
        "time": "9:00 AM",
        "goals": "Build a steady strength routine",
    }
    first = await client.post("/api/v1/bookings", json=request, headers={"Idempotency-Key": "capacity-1"})
    second = await client.post("/api/v1/bookings", json=request, headers={"Idempotency-Key": "capacity-2"})
    assert first.status_code == second.status_code == 201

    first_status = await client.patch(
        f"/api/v1/admin/bookings/{first.json()['id']}/status",
        headers=headers,
        json={"status": "CONFIRMED"},
    )
    second_status = await client.patch(
        f"/api/v1/admin/bookings/{second.json()['id']}/status",
        headers=headers,
        json={"status": "CONFIRMED"},
    )
    assert first_status.status_code == 200
    assert second_status.status_code == 409


@pytest.mark.asyncio
async def test_admin_locations_include_inactive_but_public_locations_do_not(client):
    async with app.state.test_sessions() as session:
        role = Role(name="ADMIN")
        user = User(
            full_name="Location Admin",
            email="location-admin@example.com",
            password_hash=hash_password("Strong-test-password-2026"),
            is_active=True,
            is_verified=True,
        )
        user.roles.append(role)
        active = Location(
            name="Active Studio",
            address="100 Main Street",
            city="Portland",
            state="OR",
            postal_code="97201",
            phone="5035551234",
            email="active@example.com",
            is_active=True,
        )
        inactive = Location(
            name="Inactive Studio",
            address="200 Main Street",
            city="Portland",
            state="OR",
            postal_code="97201",
            phone="5035551234",
            email="inactive@example.com",
            is_active=False,
        )
        session.add_all([user, active, inactive])
        await session.commit()

    token = (await client.post("/api/v1/auth/login", json={
        "email": "location-admin@example.com",
        "password": "Strong-test-password-2026",
    })).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    admin_response = await client.get("/api/v1/admin/locations", headers=headers)
    public_response = await client.get("/api/v1/locations")

    assert {location["name"] for location in admin_response.json()} == {"Active Studio", "Inactive Studio"}
    assert {location["name"] for location in public_response.json()} == {"Active Studio"}
    assert set(admin_response.json()[0]) == {
        "id", "name", "address", "city", "state", "postal_code", "country", "phone", "email",
        "latitude", "longitude", "opening_hours",
    }
