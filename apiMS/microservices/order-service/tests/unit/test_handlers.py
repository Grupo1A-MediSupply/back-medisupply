"""
Tests unitarios para handlers
"""
import pytest
import sys
from pathlib import Path
from uuid import uuid4
from datetime import datetime

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from shared.domain.value_objects import EntityId
from ...domain.entities import Order, OrderItem, ETA, OrderStatus
from ...application.commands import CreateOrderCommand, ConfirmOrderCommand, CancelOrderCommand
from ...application.queries import GetOrderByIdQuery
from ...application.handlers import (
    CreateOrderCommandHandler,
    ConfirmOrderCommandHandler,
    CancelOrderCommandHandler,
    GetOrderByIdQueryHandler
)


@pytest.fixture
def mock_order_repository():
    """Mock del repositorio de órdenes"""
    class MockRepository:
        def __init__(self):
            self.orders = {}
        
        async def save(self, order):
            self.orders[str(order.id)] = order
            return order
        
        async def find_by_id(self, order_id):
            return self.orders.get(str(order_id))
    
    return MockRepository()


@pytest.mark.asyncio
async def test_create_order_command_handler(mock_order_repository):
    """Test handler para crear orden"""
    handler = CreateOrderCommandHandler(mock_order_repository)
    
    command = CreateOrderCommand(
        items=[
            {"skuId": "SKU001", "qty": 2, "price": 10.0},
            {"skuId": "SKU002", "qty": 1, "price": 20.0}
        ]
    )
    
    order = await handler.handle(command)
    
    assert order is not None
    assert len(order.items) == 2
    assert order.status == OrderStatus.PLACED
    assert str(order.id) in mock_order_repository.orders


@pytest.mark.asyncio
async def test_confirm_order_command_handler(mock_order_repository):
    """Test handler para confirmar orden"""
    handler = ConfirmOrderCommandHandler(mock_order_repository)
    
    # Crear una orden
    order = Order.create(
        items=[OrderItem(sku_id="SKU001", qty=1, price=10.0)],
        status=OrderStatus.PLACED
    )
    
    # Guardar en el mock
    await mock_order_repository.save(order)
    
    # Confirmar
    command = ConfirmOrderCommand(order_id=str(order.id))
    updated_order = await handler.handle(command)
    
    assert updated_order.status == OrderStatus.CONFIRMED


@pytest.mark.asyncio
async def test_cancel_order_command_handler(mock_order_repository):
    """Test handler para cancelar orden"""
    handler = CancelOrderCommandHandler(mock_order_repository)
    
    # Crear una orden
    order = Order.create(
        items=[OrderItem(sku_id="SKU001", qty=1, price=10.0)],
        status=OrderStatus.PLACED
    )
    
    # Guardar en el mock
    await mock_order_repository.save(order)
    
    # Cancelar
    command = CancelOrderCommand(order_id=str(order.id))
    updated_order = await handler.handle(command)
    
    assert updated_order.status == OrderStatus.CANCELLED


@pytest.mark.asyncio
async def test_cancel_shipped_order_raises_error(mock_order_repository):
    """Test que no se puede cancelar orden enviada"""
    handler = CancelOrderCommandHandler(mock_order_repository)
    
    # Crear una orden y enviarla
    order = Order.create(
        items=[OrderItem(sku_id="SKU001", qty=1, price=10.0)],
        status=OrderStatus.PLACED
    )
    
    order.confirm()
    order.mark_as_picked()
    order.mark_as_shipped()
    
    await mock_order_repository.save(order)
    
    # Intentar cancelar debe lanzar error
    command = CancelOrderCommand(order_id=str(order.id))
    
    with pytest.raises(ValueError, match="No se pueden cancelar"):
        await handler.handle(command)


@pytest.mark.asyncio
async def test_get_order_by_id_query_handler(mock_order_repository):
    """Test handler para obtener orden por ID"""
    handler = GetOrderByIdQueryHandler(mock_order_repository)
    
    # Crear una orden
    order = Order.create(
        items=[OrderItem(sku_id="SKU001", qty=1, price=10.0)],
        status=OrderStatus.PLACED
    )
    
    await mock_order_repository.save(order)
    
    query = GetOrderByIdQuery(order_id=str(order.id))
    found_order = await handler.handle(query)
    
    assert found_order is not None
    assert found_order.id == order.id


@pytest.mark.asyncio
async def test_get_order_by_id_not_found(mock_order_repository):
    """Test que obtener orden inexistente lanza error"""
    handler = GetOrderByIdQueryHandler(mock_order_repository)
    
    query = GetOrderByIdQuery(order_id="non-existent-id")
    
    with pytest.raises(ValueError, match="no encontrada"):
        await handler.handle(query)


@pytest.mark.asyncio
async def test_create_order_with_eta(mock_order_repository):
    """Test crear orden con ETA"""
    handler = CreateOrderCommandHandler(mock_order_repository)
    
    command = CreateOrderCommand(
        items=[{"skuId": "SKU001", "qty": 1, "price": 10.0}],
        eta={
            "date": datetime(2024, 12, 31, 18, 0, 0),
            "windowMinutes": 60
        }
    )
    
    order = await handler.handle(command)
    
    assert order.eta is not None
    assert order.eta.window_minutes == 60


@pytest.mark.asyncio
async def test_create_order_with_reservations(mock_order_repository):
    """Test crear orden con reservas"""
    handler = CreateOrderCommandHandler(mock_order_repository)
    
    command = CreateOrderCommand(
        items=[{"skuId": "SKU001", "qty": 1, "price": 10.0}],
        reservations=["RES001", "RES002"]
    )
    
    order = await handler.handle(command)
    
    # Las reservas deben ser gestionadas por el método create
    assert order is not None

