from app.models.history import History

def test_history_action():
    history = History(
        ticket_id=1,
        user_id=2,
        action="������ ������ �� Closed"
    )
    assert "Closed" in history.action

