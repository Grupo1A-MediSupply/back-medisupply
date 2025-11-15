"""
Tests unitarios para lógica de dominio de Order
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


def test_order_add_item_combines_duplicate_skus():
    """Test que agregar item con SKU existente suma la cantidad"""
    order = Order.create(
        items=[OrderItem(sku_id="SKU001", qty=2, price=10.0)],
        status=OrderStatus.PLACED
    )
    
    new_item = OrderItem(sku_id="SKU001", qty=3, price=10.0)
    order.add_item(new_item)
    
    # Debe tener solo un item con qty=5
    assert len(order.items) == 1
    assert order.items[0].qty == 5
    assert order.items[0].sku_id == "SKU001"


def test_order_add_item_adds_new_sku():
    """Test agregar item con SKU nuevo"""
    order = Order.create(
        items=[OrderItem(sku_id="SKU001", qty=1, price=10.0)],
        status=OrderStatus.PLACED
    )
    
    new_item = OrderItem(sku_id="SKU002", qty=1, price=20.0)
    order.add_item(new_item)
    
    assert len(order.items) == 2


def test_order_add_item_updates_totals():
    """Test que agregar item actualiza totales"""
    order = Order.create(
        items=[OrderItem(sku_id="SKU001", qty=1, price=10.0)],
        status=OrderStatus.PLACED
    )
    
    initial_subtotal = order.totals["subtotal"]
    
    new_item = OrderItem(sku_id="SKU002", qty=2, price=15.0)
    order.add_item(new_item)
    
    # Subtotal debe ser 10 + (2*15) = 40
    assert order.totals["subtotal"] == 40.0


def test_order_remove_item():
    """Test remover item de orden"""
    order = Order.create(
        items=[
            OrderItem(sku_id="SKU001", qty=1, price=10.0),
            OrderItem(sku_id="SKU002", qty=1, price=20.0)
        ],
        status=OrderStatus.PLACED
    )
    
    order.remove_item("SKU001")
    
    assert len(order.items) == 1
    assert order.items[0].sku_id == "SKU002"


def test_order_remove_item_updates_totals():
    """Test que remover item actualiza totales"""
    order = Order.create(
        items=[
            OrderItem(sku_id="SKU001", qty=1, price=10.0),
            OrderItem(sku_id="SKU002", qty=1, price=20.0)
        ],
        status=OrderStatus.PLACED
    )
    
    order.remove_item("SKU001")
    
    # Debe quedar solo el item de 20
    assert order.totals["subtotal"] == 20.0


def test_order_remove_item_cannot_leave_empty():
    """Test que no se puede remover el último item"""
    order = Order.create(
        items=[OrderItem(sku_id="SKU001", qty=1, price=10.0)],
        status=OrderStatus.PLACED
    )
    
    with pytest.raises(ValueError, match="al menos un artículo"):
        order.remove_item("SKU001")


def test_order_add_item_in_non_placed_status_raises_error():
    """Test que no se pueden agregar items a orden no en estado PLACED"""
    order = Order.create(
        items=[OrderItem(sku_id="SKU001", qty=1, price=10.0)],
        status=OrderStatus.PLACED
    )
    
    order.confirm()
    
    new_item = OrderItem(sku_id="SKU002", qty=1, price=20.0)
    
    with pytest.raises(ValueError, match="PLACED"):
        order.add_item(new_item)


def test_order_remove_item_in_non_placed_status_raises_error():
    """Test que no se pueden remover items de orden no en estado PLACED"""
    order = Order.create(
        items=[OrderItem(sku_id="SKU001", qty=1, price=10.0)],
        status=OrderStatus.PLACED
    )
    
    order.confirm()
    
    with pytest.raises(ValueError, match="PLACED"):
        order.remove_item("SKU001")


def test_order_state_machine_picked():
    """Test máquina de estados: PLACED -> CONFIRMED -> PICKED"""
    order = Order.create(
        items=[OrderItem(sku_id="SKU001", qty=1, price=10.0)],
        status=OrderStatus.PLACED
    )
    
    order.confirm()
    assert order.status == OrderStatus.CONFIRMED
    
    order.mark_as_picked()
    assert order.status == OrderStatus.PICKED


def test_order_state_machine_shipped():
    """Test máquina de estados hasta SHIPPED"""
    order = Order.create(
        items=[OrderItem(sku_id="SKU001", qty=1, price=10.0)],
        status=OrderStatus.PLACED
    )
    
    order.confirm()
    order.mark_as_picked()
    order.mark_as_shipped()
    
    assert order.status == OrderStatus.SHIPPED


def test_order_state_machine_delivered():
    """Test máquina de estados completa hasta DELIVERED"""
    order = Order.create(
        items=[OrderItem(sku_id="SKU001", qty=1, price=10.0)],
        status=OrderStatus.PLACED
    )
    
    order.confirm()
    order.mark_as_picked()
    order.mark_as_shipped()
    order.mark_as_delivered()
    
    assert order.status == OrderStatus.DELIVERED


def test_order_cannot_pick_non_confirmed():
    """Test que no se puede marcar como PICKED sin estar CONFIRMED"""
    order = Order.create(
        items=[OrderItem(sku_id="SKU001", qty=1, price=10.0)],
        status=OrderStatus.PLACED
    )
    
    with pytest.raises(ValueError, match="confirmados"):
        order.mark_as_picked()


def test_order_cannot_ship_non_picked():
    """Test que no se puede enviar sin estar PICKED"""
    order = Order.create(
        items=[OrderItem(sku_id="SKU001", qty=1, price=10.0)],
        status=OrderStatus.PLACED
    )
    
    order.confirm()
    
    with pytest.raises(ValueError, match="recogidos"):
        order.mark_as_shipped()


def test_order_cannot_deliver_non_shipped():
    """Test que no se puede entregar sin estar SHIPPED"""
    order = Order.create(
        items=[OrderItem(sku_id="SKU001", qty=1, price=10.0)],
        status=OrderStatus.PLACED
    )
    
    order.confirm()
    order.mark_as_picked()
    
    with pytest.raises(ValueError, match="enviados"):
        order.mark_as_delivered()


def test_order_add_reservation():
    """Test agregar reserva a orden"""
    order = Order.create(
        items=[OrderItem(sku_id="SKU001", qty=1, price=10.0)],
        status=OrderStatus.PLACED
    )
    
    order.add_reservation("RES001")
    order.add_reservation("RES002")
    
    assert len(order.reservations) == 2
    assert "RES001" in order.reservations
    assert "RES002" in order.reservations


def test_order_add_duplicate_reservation():
    """Test que agregar reserva duplicada no duplica entradas"""
    order = Order.create(
        items=[OrderItem(sku_id="SKU001", qty=1, price=10.0)],
        status=OrderStatus.PLACED
    )
    
    order.add_reservation("RES001")
    order.add_reservation("RES001")
    
    # Solo debe estar una vez
    assert order.reservations.count("RES001") == 1


def test_order_remove_reservation():
    """Test remover reserva de orden"""
    order = Order.create(
        items=[OrderItem(sku_id="SKU001", qty=1, price=10.0)],
        status=OrderStatus.PLACED
    )
    
    order.add_reservation("RES001")
    order.add_reservation("RES002")
    
    order.remove_reservation("RES001")
    
    assert len(order.reservations) == 1
    assert "RES002" in order.reservations
    assert "RES001" not in order.reservations

