import os
from pathlib import Path
from dotenv import load_dotenv

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.database import Base
from app.main import app
from app import dependencies
from fastapi.testclient import TestClient
from app.domain.printing import PrintStrategyBase

from tests.utils.db_seed_loader import load_seeds_from_dir

# Load .env variables
load_dotenv()
APITEST_DATABASE_PATH = os.getenv("APITEST_DATABASE_PATH", None)
if APITEST_DATABASE_PATH:
    path = Path(__file__).parent.parent.parent / APITEST_DATABASE_PATH
    APITEST_DATABASE_URL = "sqlite:///" + path.as_posix()
else:
    APITEST_DATABASE_URL = "sqlite:///:memory:"


# Create test engine + session
test_engine = create_engine(
    APITEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():

    print(APITEST_DATABASE_URL)
    print("Tables before drop_all:", Base.metadata.tables.keys())
    Base.metadata.drop_all(bind=test_engine)
    print("Tables before create_all:", Base.metadata.tables.keys())
    Base.metadata.create_all(bind=test_engine)

    from app.models import StorageElement, HardwareItem, StorageType

    load_seeds_from_dir(
        TestingSessionLocal(),
        Path(__file__).parent / "seeds",
        {
            "storage_type": StorageType,
            "storage_element": StorageElement,
            "hardware_items": HardwareItem,
        },
    )

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def clear_registries():
    PrintStrategyBase.clear_registry()
    yield


# Start a transaction and roll back after each test
@pytest.fixture()
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
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
