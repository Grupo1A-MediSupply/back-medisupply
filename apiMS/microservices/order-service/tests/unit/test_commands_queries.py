"""
Tests unitarios para comandos y queries
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime

# Agregar paths al PYTHONPATH
order_service_path = str(Path(__file__).parent.parent.parent.resolve())
shared_path = str(Path(__file__).parent.parent.parent.parent.resolve() / "shared")
if order_service_path not in sys.path:
    sys.path.insert(0, order_service_path)
if shared_path not in sys.path:
    sys.path.insert(0, str(shared_path))

# Los imports se hacen dentro de las funciones para evitar problemas cuando pytest carga el módulo


def test_create_order_command():
    """Test CreateOrderCommand"""
    from application.commands import CreateOrderCommand
    command = CreateOrderCommand(
        items=[
            {"skuId": "SKU001", "qty": 2, "price": 10.0}
        ]
    )
    
    assert len(command.items) == 1
    assert command.items[0]["qty"] == 2


def test_create_order_command_with_eta():
    """Test CreateOrderCommand con ETA"""
    from application.commands import CreateOrderCommand
    command = CreateOrderCommand(
        items=[{"skuId": "SKU001", "qty": 1, "price": 10.0}],
        eta={
            "date": datetime(2024, 12, 31, 18, 0, 0),
            "windowMinutes": 60
        }
    )
    
    assert command.eta is not None
    assert command.eta["windowMinutes"] == 60


def test_update_order_command():
    """Test UpdateOrderCommand"""
    from application.commands import UpdateOrderCommand
    command = UpdateOrderCommand(
        order_id="order-123",
        items=[
            {"skuId": "SKU001", "qty": 3, "price": 10.0}
        ]
    )
    
    assert command.order_id == "order-123"
    assert len(command.items) == 1


def test_confirm_order_command():
    """Test ConfirmOrderCommand"""
    from application.commands import ConfirmOrderCommand
    command = ConfirmOrderCommand(order_id="order-123")
    
    assert command.order_id == "order-123"


def test_cancel_order_command():
    """Test CancelOrderCommand"""
    from application.commands import CancelOrderCommand
    command = CancelOrderCommand(order_id="order-123")
    
    assert command.order_id == "order-123"


def test_mark_order_picked_command():
    """Test MarkOrderPickedCommand"""
    from application.commands import MarkOrderPickedCommand
    command = MarkOrderPickedCommand(order_id="order-123")
    
    assert command.order_id == "order-123"


def test_mark_order_shipped_command():
    """Test MarkOrderShippedCommand"""
    from application.commands import MarkOrderShippedCommand
    command = MarkOrderShippedCommand(order_id="order-123")
    
    assert command.order_id == "order-123"


def test_mark_order_delivered_command():
    """Test MarkOrderDeliveredCommand"""
    from application.commands import MarkOrderDeliveredCommand
    command = MarkOrderDeliveredCommand(order_id="order-123")
    
    assert command.order_id == "order-123"


def test_add_reservation_command():
    """Test AddReservationCommand"""
    from application.commands import AddReservationCommand
    command = AddReservationCommand(
        order_id="order-123",
        reservation_id="res-456"
    )
    
    assert command.order_id == "order-123"
    assert command.reservation_id == "res-456"


def test_remove_reservation_command():
    """Test RemoveReservationCommand"""
    from application.commands import RemoveReservationCommand
    command = RemoveReservationCommand(
        order_id="order-123",
        reservation_id="res-456"
    )
    
    assert command.order_id == "order-123"
    assert command.reservation_id == "res-456"


def test_get_order_by_id_query():
    """Test GetOrderByIdQuery"""
    from application.queries import GetOrderByIdQuery
    query = GetOrderByIdQuery(order_id="order-123")
    
    assert query.order_id == "order-123"


def test_get_orders_by_status_query():
    """Test GetOrdersByStatusQuery"""
    from application.queries import GetOrdersByStatusQuery
    query = GetOrdersByStatusQuery(
        status="PLACED",
        skip=0,
        limit=10
    )
    
    assert query.status == "PLACED"
    assert query.skip == 0
    assert query.limit == 10


def test_get_orders_by_status_query_defaults():
    """Test GetOrdersByStatusQuery con valores por defecto"""
    from application.queries import GetOrdersByStatusQuery
    query = GetOrdersByStatusQuery(status="CONFIRMED")
    
    assert query.status == "CONFIRMED"
    assert query.skip == 0
    assert query.limit == 100


def test_get_all_orders_query():
    """Test GetAllOrdersQuery"""
    from application.queries import GetAllOrdersQuery
    query = GetAllOrdersQuery(skip=10, limit=50)
    
    assert query.skip == 10
    assert query.limit == 50


def test_get_all_orders_query_defaults():
    """Test GetAllOrdersQuery con valores por defecto"""
    from application.queries import GetAllOrdersQuery
    query = GetAllOrdersQuery()
    
    assert query.skip == 0
    assert query.limit == 100

