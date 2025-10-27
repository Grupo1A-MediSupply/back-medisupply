"""
Tests unitarios para el repositorio
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
from ...infrastructure.repositories import SQLAlchemyOrderRepository
from tests.conftest import db_session, order_repository


@pytest.mark.asyncio
async def test_save_order(db_session, order_repository):
    """Test guardar orden"""
    order = Order.create(
        items=[
            OrderItem(sku_id="SKU001", qty=2, price=10.0),
            OrderItem(sku_id="SKU002", qty=1, price=20.0)
        ],
        status=OrderStatus.PLACED
    )
    
    saved_order = await order_repository.save(order)
    
    assert saved_order.id == order.id
    assert len(saved_order.items) == 2
    assert saved_order.status == OrderStatus.PLACED


@pytest.mark.asyncio
async def test_find_order_by_id(db_session, order_repository):
    """Test buscar orden por ID"""
    order = Order.create(
        items=[OrderItem(sku_id="SKU001", qty=1, price=10.0)],
        status=OrderStatus.PLACED
    )
    
    await order_repository.save(order)
    found_order = await order_repository.find_by_id(order.id)
    
    assert found_order is not None
    assert found_order.id == order.id


@pytest.mark.asyncio
async def test_find_order_by_nonexistent_id(db_session, order_repository):
    """Test buscar orden inexistente"""
    fake_id = EntityId(str(uuid4()))
    found_order = await order_repository.find_by_id(fake_id)
    
    assert found_order is None


@pytest.mark.asyncio
async def test_find_orders_by_status(db_session, order_repository):
    """Test buscar órdenes por estado"""
    # Crear varias órdenes con diferentes estados
    order1 = Order.create(
        items=[OrderItem(sku_id="SKU001", qty=1, price=10.0)],
        status=OrderStatus.PLACED
    )
    
    order2 = Order.create(
        items=[OrderItem(sku_id="SKU002", qty=1, price=20.0)],
        status=OrderStatus.CONFIRMED
    )
    
    order3 = Order.create(
        items=[OrderItem(sku_id="SKU003", qty=1, price=30.0)],
        status=OrderStatus.PLACED
    )
    
    await order_repository.save(order1)
    await order_repository.save(order2)
    await order_repository.save(order3)
    
    # Buscar órdenes PLACED
    placed_orders = await order_repository.find_by_status(OrderStatus.PLACED)
    
    assert len(placed_orders) == 2
    assert all(o.status == OrderStatus.PLACED for o in placed_orders)


@pytest.mark.asyncio
async def test_save_order_with_reservations(db_session, order_repository):
    """Test guardar orden con reservas"""
    order = Order.create(
        items=[OrderItem(sku_id="SKU001", qty=1, price=10.0)],
        status=OrderStatus.PLACED
    )
    
    order.add_reservation("RES001")
    order.add_reservation("RES002")
    
    saved_order = await order_repository.save(order)
    
    assert len(saved_order.reservations) == 2
    assert "RES001" in saved_order.reservations
    assert "RES002" in saved_order.reservations


@pytest.mark.asyncio
async def test_save_order_with_eta(db_session, order_repository):
    """Test guardar orden con ETA"""
    eta = ETA(
        date=datetime.now() + timedelta(days=7),
        window_minutes=60
    )
    
    order = Order.create(
        items=[OrderItem(sku_id="SKU001", qty=1, price=10.0)],
        eta=eta,
        status=OrderStatus.PLACED
    )
    
    saved_order = await order_repository.save(order)
    
    assert saved_order.eta is not None
    assert saved_order.eta.window_minutes == 60


@pytest.mark.asyncio
async def test_update_order(db_session, order_repository):
    """Test actualizar orden"""
    order = Order.create(
        items=[OrderItem(sku_id="SKU001", qty=1, price=10.0)],
        status=OrderStatus.PLACED
    )
    
    saved_order = await order_repository.save(order)
    
    # Actualizar estado
    saved_order.confirm()
    
    updated_order = await order_repository.save(saved_order)
    
    assert updated_order.status == OrderStatus.CONFIRMED


@pytest.mark.asyncio
async def test_update_order_items(db_session, order_repository):
    """Test actualizar items de orden"""
    order = Order.create(
        items=[
            OrderItem(sku_id="SKU001", qty=1, price=10.0)
        ],
        status=OrderStatus.PLACED
    )
    
    saved_order = await order_repository.save(order)
    
    # Agregar nuevo item
    new_item = OrderItem(sku_id="SKU002", qty=2, price=15.0)
    saved_order.add_item(new_item)
    
    updated_order = await order_repository.save(saved_order)
    
    assert len(updated_order.items) == 2
    assert any(item.sku_id == "SKU002" for item in updated_order.items)


@pytest.mark.asyncio
async def test_delete_order(db_session, order_repository):
    """Test eliminar orden"""
    order = Order.create(
        items=[OrderItem(sku_id="SKU001", qty=1, price=10.0)],
        status=OrderStatus.PLACED
    )
    
    saved_order = await order_repository.save(order)
    result = await order_repository.delete(saved_order.id)
    
    assert result is True
    
    # Verificar que no existe
    found_order = await order_repository.find_by_id(saved_order.id)
    assert found_order is None


@pytest.mark.asyncio
async def test_exists_by_id(db_session, order_repository):
    """Test verificar existencia de orden"""
    order = Order.create(
        items=[OrderItem(sku_id="SKU001", qty=1, price=10.0)],
        status=OrderStatus.PLACED
    )
    
    saved_order = await order_repository.save(order)
    exists = await order_repository.exists_by_id(saved_order.id)
    
    assert exists is True


@pytest.mark.asyncio
async def test_find_all_orders(db_session, order_repository):
    """Test listar todas las órdenes"""
    # Crear múltiples órdenes
    for i in range(5):
        order = Order.create(
            items=[OrderItem(sku_id=f"SKU{i:03d}", qty=1, price=10.0)],
            status=OrderStatus.PLACED
        )
        await order_repository.save(order)
    
    all_orders = await order_repository.find_all(skip=0, limit=10)
    
    assert len(all_orders) == 5


@pytest.mark.asyncio
async def test_find_all_orders_with_pagination(db_session, order_repository):
    """Test listar órdenes con paginación"""
    # Crear múltiples órdenes
    for i in range(10):
        order = Order.create(
            items=[OrderItem(sku_id=f"SKU{i:03d}", qty=1, price=10.0)],
            status=OrderStatus.PLACED
        )
        await order_repository.save(order)
    
    # Primera página
    page1 = await order_repository.find_all(skip=0, limit=5)
    assert len(page1) == 5
    
    # Segunda página
    page2 = await order_repository.find_all(skip=5, limit=5)
    assert len(page2) == 5
    
    # Las páginas no deben compartir órdenes
    page1_ids = {str(o.id) for o in page1}
    page2_ids = {str(o.id) for o in page2}
    assert page1_ids.isdisjoint(page2_ids)

