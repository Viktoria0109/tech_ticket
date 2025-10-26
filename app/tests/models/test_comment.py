# -*- coding: utf-8 -*-

from app.models import Comment

def test_comment_text():
    comment = Comment(
        user_id=1,
        ticket_id=2,
        text="Проблема решена"
    )
    assert comment.text == "Проблема решена"

