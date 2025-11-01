# -*- coding: utf-8 -*-
from app.models import Notification

def test_notification_creation():
    notification = Notification(
        user_id=1,
        ticket_id=2,
        message="Назначен новый исполнитель",
        is_read=False
    )
    assert notification.user_id == 1
    assert notification.is_read is False
    assert "исполнитель" in notification.message

