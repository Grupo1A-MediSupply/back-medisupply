"""
Tests unitarios para el repositorio
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
from ...domain.entities import Route, Stop, ETA, RouteStatus
from ...infrastructure.repositories import SQLAlchemyLogisticsRepository
from tests.conftest import db_session, logistics_repository


@pytest.mark.asyncio
async def test_save_route(db_session, logistics_repository):
    """Test guardar ruta"""
    route = Route.create(
        stops=[
            Stop(order_id="ORD001", priority=1),
            Stop(order_id="ORD002", priority=2)
        ],
        vehicle_id="VEH001"
    )
    
    saved_route = await logistics_repository.save(route)
    
    assert saved_route.id == route.id
    assert len(saved_route.stops) == 2
    assert saved_route.status == RouteStatus.PLANNED


@pytest.mark.asyncio
async def test_find_route_by_id(db_session, logistics_repository):
    """Test buscar ruta por ID"""
    route = Route.create(
        stops=[Stop(order_id="ORD001", priority=1)]
    )
    
    await logistics_repository.save(route)
    found_route = await logistics_repository.find_by_id(route.id)
    
    assert found_route is not None
    assert found_route.id == route.id


@pytest.mark.asyncio
async def test_find_routes_by_vehicle(db_session, logistics_repository):
    """Test buscar rutas por vehículo"""
    # Crear varias rutas con diferentes vehículos
    route1 = Route.create(
        stops=[Stop(order_id="ORD001", priority=1)],
        vehicle_id="VEH001"
    )
    
    route2 = Route.create(
        stops=[Stop(order_id="ORD002", priority=1)],
        vehicle_id="VEH001"
    )
    
    route3 = Route.create(
        stops=[Stop(order_id="ORD003", priority=1)],
        vehicle_id="VEH002"
    )
    
    await logistics_repository.save(route1)
    await logistics_repository.save(route2)
    await logistics_repository.save(route3)
    
    # Buscar rutas del VEH001
    vehicle_routes = await logistics_repository.find_by_vehicle_id("VEH001")
    
    assert len(vehicle_routes) == 2
    assert all(r.vehicle_id == "VEH001" for r in vehicle_routes)


@pytest.mark.asyncio
async def test_find_routes_by_status(db_session, logistics_repository):
    """Test buscar rutas por estado"""
    # Crear varias rutas con diferentes estados
    route1 = Route.create(
        stops=[Stop(order_id="ORD001", priority=1)],
        status=RouteStatus.PLANNED
    )
    
    route2 = Route.create(
        stops=[Stop(order_id="ORD002", priority=1)],
        status=RouteStatus.IN_PROGRESS
    )
    
    route3 = Route.create(
        stops=[Stop(order_id="ORD003", priority=1)],
        status=RouteStatus.PLANNED
    )
    
    await logistics_repository.save(route1)
    await logistics_repository.save(route2)
    await logistics_repository.save(route3)
    
    # Buscar rutas PLANNED
    planned_routes = await logistics_repository.find_by_status(RouteStatus.PLANNED)
    
    assert len(planned_routes) == 2
    assert all(r.status == RouteStatus.PLANNED for r in planned_routes)


@pytest.mark.asyncio
async def test_save_route_with_stops_and_eta(db_session, logistics_repository):
    """Test guardar ruta con paradas y ETA"""
    eta = ETA(
        date=datetime.now(),
        window_minutes=60
    )
    
    stops = [
        Stop(order_id="ORD001", priority=1, eta=eta),
        Stop(order_id="ORD002", priority=2)
    ]
    
    route = Route.create(stops=stops, vehicle_id="VEH001")
    
    saved_route = await logistics_repository.save(route)
    
    assert saved_route is not None
    assert len(saved_route.stops) == 2
    assert saved_route.stops[0].eta is not None


@pytest.mark.asyncio
async def test_update_route_status(db_session, logistics_repository):
    """Test actualizar estado de ruta"""
    route = Route.create(stops=[Stop(order_id="ORD001", priority=1)])
    
    saved_route = await logistics_repository.save(route)
    
    # Actualizar estado
    saved_route.start_route("VEH001")
    
    updated_route = await logistics_repository.save(saved_route)
    
    assert updated_route.status == RouteStatus.IN_PROGRESS
    assert updated_route.vehicle_id == "VEH001"


@pytest.mark.asyncio
async def test_find_all_routes(db_session, logistics_repository):
    """Test listar todas las rutas"""
    # Crear múltiples rutas
    for i in range(5):
        route = Route.create(
            stops=[Stop(order_id=f"ORD{i:03d}", priority=1)]
        )
        await logistics_repository.save(route)
    
    all_routes = await logistics_repository.find_all(skip=0, limit=10)
    
    assert len(all_routes) == 5


@pytest.mark.asyncio
async def test_find_all_routes_with_pagination(db_session, logistics_repository):
    """Test listar rutas con paginación"""
    # Crear múltiples rutas
    for i in range(10):
        route = Route.create(
            stops=[Stop(order_id=f"ORD{i:03d}", priority=1)]
        )
        await logistics_repository.save(route)
    
    # Primera página
    page1 = await logistics_repository.find_all(skip=0, limit=5)
    assert len(page1) == 5
    
    # Segunda página
    page2 = await logistics_repository.find_all(skip=5, limit=5)
    assert len(page2) == 5


@pytest.mark.asyncio
async def test_delete_route(db_session, logistics_repository):
    """Test eliminar ruta"""
    route = Route.create(stops=[Stop(order_id="ORD001", priority=1)])
    
    saved_route = await logistics_repository.save(route)
    result = await logistics_repository.delete(saved_route.id)
    
    assert result is True
    
    # Verificar que no existe
    found_route = await logistics_repository.find_by_id(saved_route.id)
    assert found_route is None


@pytest.mark.asyncio
async def test_exists_by_id(db_session, logistics_repository):
    """Test verificar existencia de ruta"""
    route = Route.create(stops=[Stop(order_id="ORD001", priority=1)])
    
    saved_route = await logistics_repository.save(route)
    exists = await logistics_repository.exists_by_id(saved_route.id)
    
    assert exists is True

