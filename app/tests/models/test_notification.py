from app.models.notification import Notification

def test_notification_creation():
    note = Notification(
        user_id=1,
        ticket_id=2,
        message="Ќазначен новый исполнитель"
    )
    assert note.is_read is False
    assert "исполнитель" in note.message

