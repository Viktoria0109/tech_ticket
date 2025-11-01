# -*- coding: utf-8 -*-
from app.models import Ticket

def test_ticket_defaults():
    ticket = Ticket(
        title="Ошибка входа",
        description="Пользователь не может авторизоваться",
        status="New",
        is_deleted=False
    )
    assert ticket.status == "New"
    assert ticket.is_deleted is False

