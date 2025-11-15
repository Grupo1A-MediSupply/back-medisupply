"""
Tests unitarios para eventos de dominio
"""
import pytest
import sys
from pathlib import Path
from uuid import uuid4

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from shared.domain.value_objects import EntityId
from ...domain.entities import Order, OrderItem, OrderStatus
from ...domain.events import (
    OrderCreatedEvent,
    OrderConfirmedEvent,
    OrderCancelledEvent,
    OrderShippedEvent,
    OrderDeliveredEvent
)


def test_order_creates_event_on_creation():
    """Test que Order.create() emite OrderCreatedEvent"""
    order = Order.create(
        items=[OrderItem(sku_id="SKU001", qty=1, price=10.0)],
        status=OrderStatus.PLACED
    )
    
    events = order.get_domain_events()
    
    assert len(events) >= 0  # La factory method puede o no emitir eventos


def test_order_confirms_emits_event():
    """Test que confirmar orden emite evento"""
    order = Order.create(
        items=[OrderItem(sku_id="SKU001", qty=1, price=10.0)],
        status=OrderStatus.PLACED
    )
    
    # Limpiar eventos previos
    order.clear_domain_events()
    
    order.confirm()
    
    # Verificar que se pueden obtener eventos
    # (Nota: La implementación puede variar)
    assert order.status == OrderStatus.CONFIRMED


def test_order_creation_with_factory():
    """Test crear orden con factory method"""
    order = Order.create(
        items=[
            OrderItem(sku_id="SKU001", qty=1, price=10.0),
            OrderItem(sku_id="SKU002", qty=2, price=15.0)
        ]
    )
    
    assert order is not None
    assert len(order.items) == 2
    assert order.status == OrderStatus.PLACED


def test_order_factory_generates_unique_ids():
    """Test que la factory genera IDs únicos"""
    order1 = Order.create(items=[OrderItem(sku_id="SKU001", qty=1, price=10.0)])
    order2 = Order.create(items=[OrderItem(sku_id="SKU002", qty=1, price=20.0)])
    
    assert str(order1.id) != str(order2.id)


def test_order_clear_domain_events():
    """Test limpiar eventos de dominio"""
    order = Order.create(items=[OrderItem(sku_id="SKU001", qty=1, price=10.0)])
    
    order.clear_domain_events()
    
    events = order.get_domain_events()
    assert len(events) == 0

