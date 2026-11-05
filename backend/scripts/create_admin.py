import asyncio
import getpass

from pydantic import EmailStr, TypeAdapter
from sqlalchemy import select

from app.core.security import hash_password
from app.database.session import SessionLocal
from app.models import Role, User


async def create_admin() -> None:
    name = input("Administrator name: ").strip()
    email = TypeAdapter(EmailStr).validate_python(input("Administrator email: ").strip()).lower()
    password = getpass.getpass("Password (minimum 12 characters): ")
    if len(name) < 2 or len(password) < 12:
        raise ValueError("A valid name and password of at least 12 characters are required")
    async with SessionLocal() as session:
        existing = await session.scalar(select(User).where(User.email == email))
        if existing:
            raise ValueError("An account already exists for that email")
        role = await session.scalar(select(Role).where(Role.name == "SUPER_ADMIN"))
        if role is None:
            role = Role(name="SUPER_ADMIN")
            session.add(role)
            await session.flush()
        user = User(full_name=name, email=email, password_hash=hash_password(password), is_active=True, is_verified=True)
        user.roles.append(role)
        session.add(user)
        await session.commit()
        print(f"Created administrator account {email}")


if __name__ == "__main__":
    asyncio.run(create_admin())
