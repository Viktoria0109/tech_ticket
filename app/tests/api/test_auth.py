import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.user import UserCreate
from app.schemas.auth import Token

client = TestClient(app)

def test_register_user_success(mocker):
    mock_db = mocker.Mock()
    mocker.patch("app.api.v1.auth.get_db", return_value=lambda: mock_db)
    mocker.patch("app.api.v1.auth.get_user_by_email", return_value=None)
    mocker.patch("app.api.v1.auth.create_user", return_value=mocker.Mock(id=123))

    response = client.post("/api/v1/register", json={
    "name": "Test User",
    "email": "test@example.com",
    "password": "securepassword",
    "role": 1 
})

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Пользователь успешно создан"
    assert isinstance(data["user_id"], int)


def test_register_user_exists(client, mocker):
    mock_db = mocker.Mock()
    mock_user = mocker.Mock()
    mock_user.email = "test@example.com"
    mock_user.name = "Test User"
    mock_user.role = 1
    mock_user.hashed_password = "hashed_securepassword"

    mocker.patch("app.api.v1.auth.get_db", return_value=mock_db)
    mocker.patch("app.api.v1.auth.get_user_by_email", return_value=mock_user)

    response = client.post("/api/v1/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "securepassword",
        "role": 1
    })

    assert response.status_code == 400
    assert response.json()["detail"] == "Пользователь с таким email уже существует"



def test_login_success(mocker):
    mock_db = mocker.Mock()
    mock_user = mocker.Mock(email="test@example.com", hashed_password="hashed")
    mocker.patch("app.api.v1.auth.get_db", return_value=lambda: mock_db)
    mocker.patch("app.api.v1.auth.get_user_by_email", return_value=mock_user)
    mocker.patch("app.api.v1.auth.verify_password", return_value=True)
    mocker.patch("app.api.v1.auth.create_access_token", return_value="mocked_token")

    response = client.post("api/v1/login", data={
        "username": "test@example.com",
        "password": "securepassword"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] == "mocked_token"
    assert data["token_type"] == "bearer"

def test_login_wrong_password(mocker):
    mock_db = mocker.Mock()
    mock_user = mocker.Mock(email="test@example.com", hashed_password="hashed")
    mocker.patch("app.api.v1.auth.get_db", return_value=lambda: mock_db)
    mocker.patch("app.api.v1.auth.get_user_by_email", return_value=mock_user)
    mocker.patch("app.api.v1.auth.verify_password", return_value=False)

    response = client.post("api/v1/login", data={
        "username": "test@example.com",
        "password": "wrongpassword"
    })

    assert response.status_code == 401
    assert response.json()["detail"] == "Неверный email или пароль"

