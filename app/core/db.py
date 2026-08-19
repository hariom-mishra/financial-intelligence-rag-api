from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from core.setttings import settings
from core.exceptions import DatabaseConnectionError


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
    pass


db_engine = create_async_engine(settings.DB_URL)

session = async_sessionmaker(db_engine)


async def get_db():
    try: 
        db = session()
    except Exception as e:
        raise DatabaseConnectionError(str(e))
    try:
        async with db:
            yield db
    except DatabaseConnectionError as e:
        raise e
    except Exception as e:
        raise
