from app.api.v1.admin import create_admin_if_not_exists 
from app.models import User


def test_create_admin_if_not_exists_creates_admin(mocker):
    
    mock_db = mocker.Mock()

    mocker.patch("app.api.v1.admin.SessionLocal", return_value=mock_db)

    mock_query = mocker.Mock()
    mock_filter = mocker.Mock()
    mock_filter.first.return_value = None
    mock_query.filter.return_value = mock_filter
    mock_db.query.return_value = mock_query

    create_admin_if_not_exists()

    assert mock_db.add.called
    assert mock_db.commit.called


def test_create_admin_if_not_exists_skips_if_exists(mocker):
    mock_db = mocker.Mock()
    mocker.patch("app.api.v1.admin.SessionLocal", return_value=mock_db)

    mock_query = mocker.Mock()
    mock_filter = mocker.Mock()
    mock_filter.first.return_value = User(email="admin@example.com")
    mock_query.filter.return_value = mock_filter
    mock_db.query.return_value = mock_query

    create_admin_if_not_exists()

  
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()
