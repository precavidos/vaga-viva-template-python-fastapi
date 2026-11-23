from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session

from app.config import get_settings


class Base(DeclarativeBase):
    """Base dos modelos do SQLAlchemy."""


def sqlalchemy_url(database_url: str) -> str:
    """Usa o driver psycopg 3 para URLs como `postgresql://usuario:senha@host:5432/banco`."""
    for prefix in ("postgresql://", "postgres://"):
        if database_url.startswith(prefix):
            return "postgresql+psycopg://" + database_url.removeprefix(prefix)
    return database_url


@lru_cache
def get_engine() -> Engine:
    return create_engine(sqlalchemy_url(get_settings().database_url), pool_pre_ping=True)


def get_session() -> Iterator[Session]:
    """Dependência do FastAPI que abre uma sessão do SQLAlchemy por requisição (`Depends(get_session)`)."""
    with Session(get_engine()) as session:
        yield session
