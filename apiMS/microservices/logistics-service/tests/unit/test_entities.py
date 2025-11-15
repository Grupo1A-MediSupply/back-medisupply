"""
Tests unitarios para entidades
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
from ...domain.entities import Route, Stop, ETA, Position, RouteStatus


def test_create_route_with_stops():
    """Test crear ruta con paradas"""
    route_id = EntityId(str(uuid4()))
    
    stops = [
        Stop(order_id="ORD001", priority=1),
        Stop(order_id="ORD002", priority=2)
    ]
    
    route = Route(
        route_id=route_id,
        stops=stops,
        status=RouteStatus.PLANNED
    )
    
    assert route.id == route_id
    assert len(route.stops) == 2
    assert route.status == RouteStatus.PLANNED


def test_create_route_with_empty_stops_raises_error():
    """Test que crear ruta sin paradas lanza error"""
    route_id = EntityId(str(uuid4()))
    
    with pytest.raises(ValueError, match="al menos una parada"):
        Route(
            route_id=route_id,
            stops=[],
            status=RouteStatus.PLANNED
        )


def test_add_stop_to_route():
    """Test agregar parada a ruta"""
    route_id = EntityId(str(uuid4()))
    stops = [Stop(order_id="ORD001", priority=1)]
    
    route = Route(
        route_id=route_id,
        stops=stops,
        status=RouteStatus.PLANNED
    )
    
    new_stop = Stop(order_id="ORD002", priority=2)
    route.add_stop(new_stop)
    
    assert len(route.stops) == 2
    # Las paradas deben estar ordenadas por prioridad
    assert route.stops[0].order_id == "ORD001"
    assert route.stops[1].order_id == "ORD002"


def test_add_stop_orders_by_priority():
    """Test que agregar parada ordena por prioridad"""
    route_id = EntityId(str(uuid4()))
    stops = [Stop(order_id="ORD001", priority=3)]
    
    route = Route(
        route_id=route_id,
        stops=stops,
        status=RouteStatus.PLANNED
    )
    
    # Agregar parada con prioridad 1
    route.add_stop(Stop(order_id="ORD002", priority=1))
    
    # Agregar parada con prioridad 2
    route.add_stop(Stop(order_id="ORD003", priority=2))
    
    # Debe estar ordenado: ORD002 (1), ORD003 (2), ORD001 (3)
    assert route.stops[0].order_id == "ORD002"
    assert route.stops[1].order_id == "ORD003"
    assert route.stops[2].order_id == "ORD001"


def test_remove_stop_from_route():
    """Test eliminar parada de ruta"""
    route_id = EntityId(str(uuid4()))
    stops = [
        Stop(order_id="ORD001", priority=1),
        Stop(order_id="ORD002", priority=2)
    ]
    
    route = Route(
        route_id=route_id,
        stops=stops,
        status=RouteStatus.PLANNED
    )
    
    route.remove_stop("ORD002")
    
    assert len(route.stops) == 1
    assert route.stops[0].order_id == "ORD001"


def test_remove_last_stop_raises_error():
    """Test que no se puede remover la última parada"""
    route_id = EntityId(str(uuid4()))
    stops = [Stop(order_id="ORD001", priority=1)]
    
    route = Route(
        route_id=route_id,
        stops=stops,
        status=RouteStatus.PLANNED
    )
    
    with pytest.raises(ValueError, match="al menos una parada"):
        route.remove_stop("ORD001")


def test_start_route():
    """Test iniciar ruta"""
    route_id = EntityId(str(uuid4()))
    stops = [Stop(order_id="ORD001", priority=1)]
    
    route = Route(
        route_id=route_id,
        stops=stops,
        status=RouteStatus.PLANNED
    )
    
    route.start_route("VEH001")
    
    assert route.status == RouteStatus.IN_PROGRESS
    assert route.vehicle_id == "VEH001"


def test_start_non_planned_route_raises_error():
    """Test que no se puede iniciar ruta no planificada"""
    route_id = EntityId(str(uuid4()))
    stops = [Stop(order_id="ORD001", priority=1)]
    
    route = Route(
        route_id=route_id,
        stops=stops,
        status=RouteStatus.IN_PROGRESS
    )
    
    with pytest.raises(ValueError, match="planificadas"):
        route.start_route("VEH001")


def test_complete_route():
    """Test completar ruta"""
    route_id = EntityId(str(uuid4()))
    stops = [Stop(order_id="ORD001", priority=1)]
    
    route = Route(
        route_id=route_id,
        stops=stops,
        status=RouteStatus.IN_PROGRESS
    )
    
    route.complete_route()
    
    assert route.status == RouteStatus.COMPLETED


def test_complete_non_in_progress_route_raises_error():
    """Test que no se puede completar ruta no en progreso"""
    route_id = EntityId(str(uuid4()))
    stops = [Stop(order_id="ORD001", priority=1)]
    
    route = Route(
        route_id=route_id,
        stops=stops,
        status=RouteStatus.PLANNED
    )
    
    with pytest.raises(ValueError, match="en progreso"):
        route.complete_route()


def test_cancel_route():
    """Test cancelar ruta"""
    route_id = EntityId(str(uuid4()))
    stops = [Stop(order_id="ORD001", priority=1)]
    
    route = Route(
        route_id=route_id,
        stops=stops,
        status=RouteStatus.PLANNED
    )
    
    route.cancel_route()
    
    assert route.status == RouteStatus.CANCELLED


def test_cancel_completed_route_raises_error():
    """Test que no se puede cancelar ruta completada"""
    route_id = EntityId(str(uuid4()))
    stops = [Stop(order_id="ORD001", priority=1)]
    
    route = Route(
        route_id=route_id,
        stops=stops,
        status=RouteStatus.COMPLETED
    )
    
    with pytest.raises(ValueError, match="completadas"):
        route.cancel_route()


def test_route_stop_with_eta():
    """Test parada con ETA"""
    eta = ETA(
        date=datetime(2024, 12, 31, 18, 0, 0),
        window_minutes=60
    )
    
    stop = Stop(order_id="ORD001", priority=1, eta=eta)
    
    assert stop.order_id == "ORD001"
    assert stop.eta is not None
    assert stop.eta.window_minutes == 60


def test_position_creation():
    """Test crear posición GPS"""
    position = Position(
        lat=19.4326,
        lon=-99.1332,
        timestamp=datetime.now()
    )
    
    assert position.lat == 19.4326
    assert position.lon == -99.1332


def test_position_invalid_lat_raises_error():
    """Test que latitud inválida lanza error"""
    with pytest.raises(ValueError, match="Latitud"):
        Position(lat=100, lon=0, timestamp=datetime.now())


def test_position_invalid_lon_raises_error():
    """Test que longitud inválida lanza error"""
    with pytest.raises(ValueError, match="Longitud"):
        Position(lat=0, lon=200, timestamp=datetime.now())

