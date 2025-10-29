from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_ticket_success(client, mocker):
    mock_db = mocker.Mock()
    mock_user = mocker.Mock()
    mock_user.id = 1

    mocker.patch("app.api.v1.tickets.get_db", return_value=mock_db)
    mocker.patch("app.api.v1.tickets.get_user_by_email", return_value=mock_user)

    response = client.post("/api/v1/tickets", json={
        "title": "Test",
        "description": "Unaware outlook",
        "status": "New",
        "assigned_to": 2,         
        "user_id": mock_user.id  
    })

    assert response.status_code in [200, 201]
    data = response.json()
    assert data["title"] == "Test"
    assert data["user_id"] == mock_user.id



def test_list_tickets_success(mocker, client):

    ticket = {
        "id": 1,
        "title": "Test ",
        "description": "This is a test ticket",
        "status": "New",
        "assigned_to": 2,
        
    }

    mocker.patch("app.api.v1.tickets.get_db", return_value=lambda: mocker.Mock())
    mocker.patch("app.api.v1.tickets.list_tickets", return_value=[ticket])

    response = client.get("/api/v1/tickets")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1

    first = data[0]
    assert first["id"] == 1
    assert first["title"] == "Test "
    assert first["description"] == "This is a test ticket"
    assert first["status"] == "New"
    assert first["assigned_to"] == 2
    
def test_delete_ticket_success(mocker):
    mock_db = mocker.Mock()
    mock_deleted = mocker.Mock(deleted_at="2025-10-26T10:00:00")
    mocker.patch("app.api.v1.tickets.get_db", return_value=lambda: mock_db)
    mocker.patch("app.api.v1.tickets.require_role", return_value=lambda: True)
    mocker.patch("app.api.v1.tickets.soft_delete_ticket", return_value=mock_deleted)

    response = client.delete("/api/v1/1?confirm=true")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "deleted_at" in data

def test_delete_ticket_not_found(mocker):
    mock_db = mocker.Mock()
    mocker.patch("app.api.v1.tickets.get_db", return_value=lambda: mock_db)
    mocker.patch("app.api.v1.tickets.require_role", return_value=lambda: True)
    mocker.patch("app.api.v1.tickets.crud_ticket.soft_delete_ticket", return_value=None)

    response = client.delete("/api/v1/999?confirm=true")
    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"
