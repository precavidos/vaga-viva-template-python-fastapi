"""Infraestrutura dos testes: PostgreSQL com testcontainers, migrações do Alembic e a aplicação de teste."""

import os
from collections.abc import Iterator

import pytest
from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.testclient import TestClient
from testcontainers.community.postgres import PostgresContainer

from app.config import get_settings
from app.database import get_engine
from app.main import create_app
from app.reminders.dependencies import get_email_sender, get_sms_sender
from tests.support.api import Api
from tests.support.database import Database
from tests.support.missions import PROJECT_ROOT
from tests.support.recording_senders import RecordingEmailSender, RecordingSmsSender
from tests.support.users import SECURITY_USERS_FILE

POSTGRES_IMAGE = "postgres:17-alpine"


def apply_migrations() -> None:
    config = Config(str(PROJECT_ROOT / "alembic.ini"))
    config.attributes["configure_logger"] = False
    try:
        command.upgrade(config, "heads")
    except Exception as error:
        pytest.fail(
            "não foi possível aplicar as migrações de migrations/versions (alembic upgrade heads): "
            f"{type(error).__name__}: {error}",
            pytrace=False,
        )


@pytest.fixture(scope="session")
def database_url() -> Iterator[str]:
    """Sobe um PostgreSQL, compartilhado por todos os testes, e aplica as migrações do Alembic."""
    with PostgresContainer(
        POSTGRES_IMAGE, username="clinic", password="clinic", dbname="clinic", driver=None
    ) as postgres:
        url = postgres.get_connection_url()
        os.environ["DATABASE_URL"] = url
        os.environ["CLINIC_SECURITY_USERS_FILE"] = str(PROJECT_ROOT / SECURITY_USERS_FILE)
        get_settings.cache_clear()
        get_engine.cache_clear()
        apply_migrations()
        yield url
        get_engine().dispose()


@pytest.fixture
def db(database_url: str) -> Iterator[Database]:
    """Banco de teste, com todas as tabelas esvaziadas antes de cada teste."""
    database = Database(database_url)
    database.reset()
    yield database
    database.close()


@pytest.fixture
def emails() -> RecordingEmailSender:
    return RecordingEmailSender()


@pytest.fixture
def sms() -> RecordingSmsSender:
    return RecordingSmsSender()


@pytest.fixture
def app(db: Database, emails: RecordingEmailSender, sms: RecordingSmsSender) -> FastAPI:
    """A aplicação de `create_app()`, com os envios de e-mail e SMS trocados por fakes."""
    application = create_app()
    application.dependency_overrides[get_email_sender] = lambda: emails
    application.dependency_overrides[get_sms_sender] = lambda: sms
    return application


@pytest.fixture
def api(app: FastAPI) -> Iterator[Api]:
    with TestClient(app) as client:
        yield Api(client)
