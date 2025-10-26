from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_ticket_success(mocker):
    mock_db = mocker.Mock()
    mock_ticket = mocker.Mock(id=1, title="Test", description="Desc", deleted_at=None)
    mocker.patch("app.api.tickets.get_db", return_value=lambda: mock_db)
    mocker.patch("app.api.tickets.crud_ticket.create_ticket", return_value=mock_ticket)

    response = client.post("/tickets", json={
        "title": "Test",
        "description": "Desc"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Test"
    assert data["description"] == "Desc"

def test_list_tickets_success(mocker):
    mock_db = mocker.Mock()
    mock_ticket = mocker.Mock(id=1, title="Test", description="Desc", deleted_at=None)
    mocker.patch("app.api.tickets.get_db", return_value=lambda: mock_db)
    mocker.patch("app.api.tickets.crud_ticket.list_tickets", return_value=[mock_ticket])

    response = client.get("/tickets")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["title"] == "Test"

def test_delete_ticket_success(mocker):
    mock_db = mocker.Mock()
    mock_deleted = mocker.Mock(deleted_at="2025-10-26T10:00:00")
    mocker.patch("app.api.tickets.get_db", return_value=lambda: mock_db)
    mocker.patch("app.api.tickets.require_role", return_value=lambda: True)
    mocker.patch("app.api.tickets.crud_ticket.soft_delete_ticket", return_value=mock_deleted)

    response = client.delete("/1?confirm=true")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "deleted_at" in data

def test_delete_ticket_not_found(mocker):
    mock_db = mocker.Mock()
    mocker.patch("app.api.tickets.get_db", return_value=lambda: mock_db)
    mocker.patch("app.api.tickets.require_role", return_value=lambda: True)
    mocker.patch("app.api.tickets.crud_ticket.soft_delete_ticket", return_value=None)

    response = client.delete("/999?confirm=true")
    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"
