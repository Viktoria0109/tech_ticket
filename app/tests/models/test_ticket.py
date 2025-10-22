from app.models.ticket import Ticket

def test_ticket_defaults():
    ticket = Ticket(
        title="������ �����",
        description="������������ �� ����� ��������������",
        status="New",
        priority="High"
    )
    assert ticket.status == "New"
    assert ticket.priority == "High"
    assert ticket.is_deleted is False

