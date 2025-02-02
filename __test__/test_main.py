from typing import List
from fastapi import status
from fastapi.testclient import TestClient
import jwt
from models import Answer, Memory, Sentence, User, SQLModel, Word
from sqlmodel import create_engine, select, Session
from sqlmodel.pool import StaticPool
from main import app
from routers.api import get_session
import pytest
from parsers import seed_test_data, parse_memory_data
from config import Settings

BAD_PASSWORD = "test-password-123"

SECRET_KEY = Settings().jwt_secret_key
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 30

test_data = seed_test_data()


@pytest.fixture(name="memories")
def memories_fixture():
    return test_data["memories"]


@pytest.fixture(name="words")
def words_fixture():
    return test_data["words"]


@pytest.fixture(name="sentences")
def sentences_fixture():
    return test_data["sentences"]


@pytest.fixture(name="session")
def session_fixture(
    memories: List[Memory], words: List[Word], sentences: List[Sentence]
):
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        session.add_all(memories)
        session.add_all(words)
        session.add_all(sentences)
        session.commit()
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    response = client.post(
        "/api/register", data={"username": "admin", "password": BAD_PASSWORD}
    )
    assert response.status_code == status.HTTP_201_CREATED

    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="user")
def user_fixture():
    return {"username": "testuser", "password": BAD_PASSWORD}


def _get_token(client, username):
    payload = {"username": username, "password": BAD_PASSWORD}
    response = client.post("/api/token", data=payload)
    return response


# Helper to authenticate and set cookie
def authenticate_with_cookie(client, username):
    response = _get_token(client, username)
    token = response.json()["access_token"]

    # Set the token as an HTTP-only cookie
    client.cookies.set("Authorization", f"Bearer {token}")
    return token


def test_get_token_success(client):
    resp = _get_token(client, "admin")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert "access_token" in data
    assert len(data["access_token"]) == 124
    assert data["token_type"] == "bearer"


def test_token_decode(client):
    response = _get_token(client, "admin")
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in data.keys()
    access_token = data["access_token"]
    assert access_token is not None
    decoded = jwt.decode(access_token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
    assert decoded["sub"] == "admin"


def test_create_user(user: dict, client: TestClient):
    response = client.post("/api/user/create", json=user)
    data = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    assert data["username"] == user["username"]


def test_get_user_without_auth(client):
    response = client.get("/api/user/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


def test_registration(client: TestClient, session: Session):
    payload = {"username": "newuser", "password": "test-password-123"}
    response = client.post("/api/register", data=payload)
    data = response.json()
    assert data["message"] == f"Created user {payload["username"]}"
    results = session.exec(
        select(User).where(User.username == payload["username"])
    ).first()
    assert results.username == payload["username"]


def test_get_next_memory(client: TestClient, memories: List[Memory]):
    authenticate_with_cookie(client, "admin")
    response = client.get("/api/review")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["memory"]["id"] == sorted(memories, key=lambda m: m.due_date)[0].id
    assert data["word"]["text"].lower() == "güey"
    assert data["word"]["text"].lower() in data["sentence"]["text"].lower()


def test_update_memory(client: TestClient, memories):
    authenticate_with_cookie(client, "admin")
    first_memory = sorted(memories, key=lambda m: m.due_date)[0]
    original_due_date = first_memory.due_date
    answer = Answer(memory_id=first_memory.id, correct=True)
    response = client.post("/api/review", json=answer.model_dump())
    assert response.status_code == status.HTTP_200_OK
    updated_memory = parse_memory_data(response.json())
    assert updated_memory.id == first_memory.id
    new_due_date = updated_memory.due_date
    assert new_due_date.day == original_due_date.day + 1
