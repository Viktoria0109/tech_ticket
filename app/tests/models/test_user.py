# -*- coding: utf-8 -*-
import pytest
from datetime import datetime
from app.models import User

def test_user_creation():
    user = User(
        email="test@example.com",
        hashed_password="hashed123",
        role=2,
        is_deleted=False
    )
    assert user.email == "test@example.com"
    assert user.role == 2
    assert user.is_deleted is False

def test_user_soft_delete(mocker):
    user = User(
        email="test@example.com",
        hashed_password="hashed123",
        role=2,
        is_deleted=False
    )
    mock_now = datetime(2025, 1, 1, 12, 0)
    mocker.patch("app.models.user.datetime", autospec=True)
    user.is_deleted = True
    user.deleted_at = mock_now
    assert user.is_deleted is True
    assert user.deleted_at == mock_now

