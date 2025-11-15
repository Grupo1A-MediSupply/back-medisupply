"""
Tests unitarios para entidades
"""
import pytest
import sys
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timedelta

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from shared.domain.value_objects import EntityId
from ...domain.entities import Order, OrderItem, ETA, OrderStatus


def test_create_order_with_items():
    """Test crear orden con items"""
    order_id = EntityId(str(uuid4()))
    
    items = [
        OrderItem(sku_id="SKU001", qty=2, price=10.0),
        OrderItem(sku_id="SKU002", qty=1, price=20.0)
    ]
    
    order = Order(
        order_id=order_id,
        items=items,
        status=OrderStatus.PLACED
    )
    
    assert order.id == order_id
    assert len(order.items) == 2
    assert order.status == OrderStatus.PLACED


def test_create_order_with_empty_items_raises_error():
    """Test que crear orden sin items lanza error"""
    order_id = EntityId(str(uuid4()))
    
    with pytest.raises(ValueError, match="al menos un artículo"):
        Order(
            order_id=order_id,
            items=[],
            status=OrderStatus.PLACED
        )


def test_add_item_to_order():
    """Test agregar item a orden"""
    order_id = EntityId(str(uuid4()))
    items = [OrderItem(sku_id="SKU001", qty=1, price=10.0)]
    
    order = Order(
        order_id=order_id,
        items=items,
        status=OrderStatus.PLACED
    )
    
    new_item = OrderItem(sku_id="SKU002", qty=2, price=15.0)
    order.add_item(new_item)
    
    assert len(order.items) == 2


def test_confirm_order():
    """Test confirmar orden"""
    order_id = EntityId(str(uuid4()))
    items = [OrderItem(sku_id="SKU001", qty=1, price=10.0)]
    
    order = Order(
        order_id=order_id,
        items=items,
        status=OrderStatus.PLACED
    )
    
    order.confirm()
    
    assert order.status == OrderStatus.CONFIRMED


def test_cancel_order():
    """Test cancelar orden"""
    order_id = EntityId(str(uuid4()))
    items = [OrderItem(sku_id="SKU001", qty=1, price=10.0)]
    
    order = Order(
        order_id=order_id,
        items=items,
        status=OrderStatus.PLACED
    )
    
    order.cancel()
    
    assert order.status == OrderStatus.CANCELLED


def test_order_totals_calculation():
    """Test cálculo de totales"""
    order_id = EntityId(str(uuid4()))
    items = [
        OrderItem(sku_id="SKU001", qty=2, price=10.0),
        OrderItem(sku_id="SKU002", qty=1, price=20.0)
    ]
    
    order = Order(
        order_id=order_id,
        items=items,
        status=OrderStatus.PLACED
    )
    
    # Subtotal = (2 * 10) + (1 * 20) = 40
    # Tax = 40 * 0.16 = 6.4
    # Total = 46.4
    totals = order.totals
    
    assert totals["subtotal"] == 40.0
    assert totals["tax"] == 6.4
    assert totals["grandTotal"] == 46.4


def test_order_mark_as_picked():
    """Test marcar orden como recogida"""
    order_id = EntityId(str(uuid4()))
    items = [OrderItem(sku_id="SKU001", qty=1, price=10.0)]
    
    order = Order(
        order_id=order_id,
        items=items,
        status=OrderStatus.PLACED
    )
    
    order.confirm()
    order.mark_as_picked()
    
    assert order.status == OrderStatus.PICKED


def test_order_mark_as_shipped():
    """Test marcar orden como enviada"""
    order_id = EntityId(str(uuid4()))
    items = [OrderItem(sku_id="SKU001", qty=1, price=10.0)]
    
    order = Order(
        order_id=order_id,
        items=items,
        status=OrderStatus.PLACED
    )
    
    order.confirm()
    order.mark_as_picked()
    order.mark_as_shipped()
    
    assert order.status == OrderStatus.SHIPPED


def test_order_mark_as_delivered():
    """Test marcar orden como entregada"""
    order_id = EntityId(str(uuid4()))
    items = [OrderItem(sku_id="SKU001", qty=1, price=10.0)]
    
    order = Order(
        order_id=order_id,
        items=items,
        status=OrderStatus.PLACED
    )
    
    order.confirm()
    order.mark_as_picked()
    order.mark_as_shipped()
    order.mark_as_delivered()
    
    assert order.status == OrderStatus.DELIVERED


def test_order_add_reservation():
    """Test agregar reserva a orden"""
    order_id = EntityId(str(uuid4()))
    items = [OrderItem(sku_id="SKU001", qty=1, price=10.0)]
    
    order = Order(
        order_id=order_id,
        items=items,
        status=OrderStatus.PLACED
    )
    
    order.add_reservation("RES001")
    assert "RES001" in order.reservations


def test_order_remove_reservation():
    """Test remover reserva de orden"""
    order_id = EntityId(str(uuid4()))
    items = [OrderItem(sku_id="SKU001", qty=1, price=10.0)]
    
    order = Order(
        order_id=order_id,
        items=items,
        status=OrderStatus.PLACED
    )
    
    order.add_reservation("RES001")
    order.remove_reservation("RES001")
    
    assert "RES001" not in order.reservations


def test_order_set_eta():
    """Test establecer ETA de orden"""
    order_id = EntityId(str(uuid4()))
    items = [OrderItem(sku_id="SKU001", qty=1, price=10.0)]
    eta = ETA(date=datetime(2024, 12, 31, 18, 0, 0), window_minutes=60)
    
    order = Order(
        order_id=order_id,
        items=items,
        status=OrderStatus.PLACED
    )
    
    order.set_eta(eta)
    
    assert order.eta is not None
    assert order.eta.window_minutes == 60

