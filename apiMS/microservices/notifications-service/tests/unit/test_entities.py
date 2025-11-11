"""
Tests unitarios para la entidad Notification
"""
from datetime import datetime
import pytest

# Los paths están configurados en conftest.py
from domain.entities.notification import (
    Notification,
    NotificationType,
    NotificationPriority,
)
from shared.domain.value_objects import EntityId


def test_notification_creation_properties():
    notification = Notification(
        notification_id=EntityId("notif_001"),
        user_id=EntityId("user_123"),
        title="Nueva Orden",
        message="Se creó la orden ORD-1001",
        notification_type=NotificationType.ORDER,
        priority=NotificationPriority.HIGH,
        is_read=False,
        link="/orders/ORD-1001",
        metadata={"order_id": "ORD-1001"},
    )

    assert str(notification.id) == "notif_001"
    assert str(notification.user_id) == "user_123"
    assert notification.title == "Nueva Orden"
    assert notification.message == "Se creó la orden ORD-1001"
    assert notification.notification_type == NotificationType.ORDER
    assert notification.priority == NotificationPriority.HIGH
    assert notification.is_read is False
    assert notification.link == "/orders/ORD-1001"
    assert notification.metadata["order_id"] == "ORD-1001"
    assert isinstance(notification.created_at, datetime)
    assert isinstance(notification.updated_at, datetime)


def test_mark_as_read_happy_path_and_idempotency_error():
    notification = Notification(
        notification_id=EntityId("n1"),
        user_id=EntityId("u1"),
        title="t",
        message="m",
        notification_type=NotificationType.SYSTEM,
    )

    # Happy path
    notification.mark_as_read()
    assert notification.is_read is True

    # Idempotency error when already read
    with pytest.raises(ValueError):
        notification.mark_as_read()


def test_mark_as_unread_happy_path_and_idempotency_error():
    notification = Notification(
        notification_id=EntityId("n2"),
        user_id=EntityId("u2"),
        title="t",
        message="m",
        notification_type=NotificationType.SYSTEM,
        is_read=True,
    )

    # Happy path
    notification.mark_as_unread()
    assert notification.is_read is False

    # Idempotency error when already unread
    with pytest.raises(ValueError):
        notification.mark_as_unread()


