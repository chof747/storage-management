import os
import subprocess
import time
from pathlib import Path
from dotenv import load_dotenv

import pytest
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from app.database import Base
from app.main import app
from app import dependencies
from fastapi.testclient import TestClient
from app.domain.printing import PrintStrategyBase

from tests.utils.db_seed_loader import load_seeds_from_dir

# Load .env variables
load_dotenv(dotenv_path=(Path(__file__).parent.parent / ".env").as_posix())
APITEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://test:test@localhost:5433/storage_management_test",
)
APITEST_DB_SCHEMA = os.getenv(
    "TEST_DB_SCHEMA", f"storage_management_test_{os.getpid()}"
)
TEST_COMPOSE_FILE = (
    Path(__file__).parent.parent.parent / "docker-compose.test.yml"
).as_posix()

if not APITEST_DATABASE_URL:
    raise RuntimeError(
        "TEST_DATABASE_URL or DATABASE_URL must be set for backend tests"
    )

if not APITEST_DATABASE_URL.startswith("postgresql"):
    raise RuntimeError(
        "Backend tests require a PostgreSQL DATABASE_URL (SQLite is no longer supported)"
    )


# Create test engine + session
test_engine = create_engine(
    APITEST_DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"options": f"-csearch_path={APITEST_DB_SCHEMA},public"},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def reset_sequences(connection):
    for table_name in ["storage_type", "storage_element", "hardware_items"]:
        connection.execute(
            text(
                f"""
                SELECT setval(
                    pg_get_serial_sequence('"{APITEST_DB_SCHEMA}"."{table_name}"', 'id'),
                    COALESCE((SELECT MAX(id) FROM "{APITEST_DB_SCHEMA}"."{table_name}"), 1),
                    true
                )
                """
            )
        )


def truncate_app_tables(connection):
    connection.execute(
        text(
            f'TRUNCATE TABLE "{APITEST_DB_SCHEMA}"."hardware_items", '
            f'"{APITEST_DB_SCHEMA}"."storage_element", '
            f'"{APITEST_DB_SCHEMA}"."storage_type" RESTART IDENTITY CASCADE'
        )
    )


def ensure_local_test_postgres() -> None:
    if os.getenv("CI"):
        return
    result = subprocess.run(
        ["docker", "compose", "-f", TEST_COMPOSE_FILE, "up", "-d"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "Failed to start local PostgreSQL test container. "
            f"stdout={result.stdout} stderr={result.stderr}"
        )


def wait_for_test_db(timeout_seconds: int = 30) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with test_engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return
        except Exception:
            time.sleep(1)
    raise RuntimeError("PostgreSQL test database did not become ready in time")


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    ensure_local_test_postgres()
    wait_for_test_db()

    with test_engine.begin() as connection:
        connection.execute(text(f'DROP SCHEMA IF EXISTS "{APITEST_DB_SCHEMA}" CASCADE'))
        connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{APITEST_DB_SCHEMA}"'))
        connection.execute(text(f'SET search_path TO "{APITEST_DB_SCHEMA}", public'))
    Base.metadata.create_all(bind=test_engine)

    from app.models import StorageElement, HardwareItem, StorageType

    seed_session = TestingSessionLocal()
    try:
        load_seeds_from_dir(
            seed_session,
            Path(__file__).parent / "seeds",
            {
                "storage_type": StorageType,
                "storage_element": StorageElement,
                "hardware_items": HardwareItem,
            },
        )
    finally:
        seed_session.close()

    with test_engine.begin() as connection:
        reset_sequences(connection)

    yield

    with test_engine.begin() as connection:
        connection.execute(text(f'DROP SCHEMA IF EXISTS "{APITEST_DB_SCHEMA}" CASCADE'))


@pytest.fixture()
def clear_registries():
    PrintStrategyBase.clear_registry()
    yield


# Start a transaction and roll back after each test
@pytest.fixture()
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()
    connection.execute(text(f'SET search_path TO "{APITEST_DB_SCHEMA}", public'))
    reset_sequences(connection)
    session = TestingSessionLocal(bind=connection)
    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def _restart_savepoint(sess, trans):
        nonlocal nested
        if trans.nested and not nested.is_active:
            nested = connection.begin_nested()

    yield session

    session.close()
    event.remove(session, "after_transaction_end", _restart_savepoint)
    if hasattr(transaction, "is_active") and transaction.is_active:
        transaction.rollback()
    connection.close()


# Use that session in a FastAPI dependency override
@pytest.fixture()
def client(db_session: Session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[dependencies.get_db] = override_get_db
    return TestClient(app)
