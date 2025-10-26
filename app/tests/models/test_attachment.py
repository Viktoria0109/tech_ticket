# -*- coding:utf-8 -*-
from app.models import Attachment

def test_attachment_path():
    attach = Attachment(
        ticket_id=1,
        file_path="app/static/uploads/test.pdf",
        uploaded_by=2
    )
    assert attach.file_path.endswith(".pdf")
    assert attach.ticket_id == 1

