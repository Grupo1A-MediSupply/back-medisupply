"""
Tests unitarios para handlers
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from shared.domain.value_objects import EntityId
from ...domain.entities import Route, Stop, RouteStatus
from ...application.commands import CreateRouteCommand, StartRouteCommand
from ...application.queries import GetRouteByIdQuery


@pytest.fixture
def mock_logistics_repository():
    """Mock del repositorio de logística"""
    class MockRepository:
        def __init__(self):
            self.routes = {}
        
        async def save(self, route):
            self.routes[str(route.id)] = route
            return route
        
        async def find_by_id(self, route_id):
            return self.routes.get(str(route_id))
    
    return MockRepository()


@pytest.mark.asyncio
async def test_create_route_command_handler(mock_logistics_repository):
    """Test handler para crear ruta"""
    from ...application.handlers import CreateRouteCommandHandler
    
    handler = CreateRouteCommandHandler(mock_logistics_repository)
    
    command = CreateRouteCommand(
        stops=[
            {"orderId": "ORD001", "priority": 1},
            {"orderId": "ORD002", "priority": 2}
        ],
        vehicle_id="VEH001"
    )
    
    route = await handler.handle(command)
    
    assert route is not None
    assert len(route.stops) == 2
    assert route.status == RouteStatus.PLANNED
    assert str(route.id) in mock_logistics_repository.routes


@pytest.mark.asyncio
async def test_start_route_command_handler(mock_logistics_repository):
    """Test handler para iniciar ruta"""
    from ...application.handlers import StartRouteCommandHandler
    
    handler = StartRouteCommandHandler(mock_logistics_repository)
    
    # Crear una ruta
    route = Route.create(
        stops=[Stop(order_id="ORD001", priority=1)],
        status=RouteStatus.PLANNED
    )
    
    # Guardar en el mock
    await mock_logistics_repository.save(route)
    
    # Iniciar
    command = StartRouteCommand(route_id=str(route.id), vehicle_id="VEH001")
    updated_route = await handler.handle(command)
    
    assert updated_route.status == RouteStatus.IN_PROGRESS
    assert updated_route.vehicle_id == "VEH001"


@pytest.mark.asyncio
async def test_get_route_by_id_handler(mock_logistics_repository):
    """Test handler para obtener ruta por ID"""
    from ...application.handlers import GetRouteByIdQueryHandler
    
    handler = GetRouteByIdQueryHandler(mock_logistics_repository)
    
    # Crear una ruta
    route = Route.create(
        stops=[Stop(order_id="ORD001", priority=1)],
        status=RouteStatus.PLANNED
    )
    
    await mock_logistics_repository.save(route)
    
    query = GetRouteByIdQuery(route_id=str(route.id))
    found_route = await handler.handle(query)
    
    assert found_route is not None
    assert found_route.id == route.id


@pytest.mark.asyncio
async def test_get_route_by_id_not_found(mock_logistics_repository):
    """Test que obtener ruta inexistente lanza error"""
    from ...application.handlers import GetRouteByIdQueryHandler
    
    handler = GetRouteByIdQueryHandler(mock_logistics_repository)
    
    query = GetRouteByIdQuery(route_id="non-existent-id")
    
    with pytest.raises(ValueError, match="no encontrada"):
        await handler.handle(query)

