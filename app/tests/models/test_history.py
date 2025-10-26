# -*- coding: utf-8 -*-
from app.models import History

def test_history_action():
    history = History(
        ticket_id=1,
        user_id=2,
        action="Статус изменён на Closed"
    )
    assert "Closed" in history.action

