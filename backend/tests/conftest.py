import pytest
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.infrastructure.database import Base, get_db
from app.main import app

from app.domain.entities import User, Board, List, Card
from app.domain.entities.tag import Tag

fake = Faker()

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def fake():
    """Fixture de Faker para inyectar en las funciones de test."""
    return Faker()


@pytest.fixture(autouse=True)
def setup_database():
    """Crea las tablas antes de cada test y las elimina al finalizar."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Sesión de base de datos aislada para usar directamente en tests."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        if transaction.is_active:
            transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session):
    """Cliente de pruebas que sobreescribe la dependencia get_db() de FastAPI."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

def _make_user(client, fake):
    password = fake.password(length=12)
    payload = {"email": fake.email(), "username": fake.user_name(), "password": password}
    assert client.post("/api/auth/register", json=payload).status_code == 201
    response = client.post(
        "/api/auth/login",
        data={"username": payload["email"], "password": password},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def auth_headers(client, fake):
    return _make_user(client, fake)


@pytest.fixture
def other_auth_headers(client, fake):
    return _make_user(client, fake)
