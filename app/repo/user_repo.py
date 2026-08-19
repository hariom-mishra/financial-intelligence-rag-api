from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from schema.users import Users


async def get_user_by_email(db: AsyncSession, email: str) -> Users | None:
    """Fetch a user by email. Returns None if not found."""
    result = await db.execute(select(Users).where(Users.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> Users | None:
    """Fetch a user by primary key. Returns None if not found."""
    result = await db.execute(select(Users).where(Users.id == user_id))
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    name: str,
    email: str,
    hashed_password: str,
    role: str = "user",
) -> Users:
    """Persist a new user and return the created instance."""
    user = Users(
        name=name,
        email=email,
        hashed_password=hashed_password,
        role=role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
