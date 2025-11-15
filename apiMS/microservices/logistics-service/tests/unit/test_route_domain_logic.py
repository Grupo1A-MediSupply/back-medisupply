"""
Tests unitarios para lógica de dominio de Route
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
from ...domain.entities import Route, Stop, RouteStatus


def test_route_state_machine_planned_to_in_progress():
    """Test máquina de estados: PLANNED -> IN_PROGRESS"""
    route = Route.create(stops=[Stop(order_id="ORD001", priority=1)])
    
    assert route.status == RouteStatus.PLANNED
    
    route.start_route("VEH001")
    
    assert route.status == RouteStatus.IN_PROGRESS
    assert route.vehicle_id == "VEH001"


def test_route_state_machine_to_completed():
    """Test máquina de estados hasta COMPLETED"""
    route = Route.create(stops=[Stop(order_id="ORD001", priority=1)])
    
    route.start_route("VEH001")
    route.complete_route()
    
    assert route.status == RouteStatus.COMPLETED


def test_route_state_machine_to_cancelled():
    """Test máquina de estados hasta CANCELLED"""
    route = Route.create(stops=[Stop(order_id="ORD001", priority=1)])
    
    route.cancel_route()
    
    assert route.status == RouteStatus.CANCELLED


def test_add_stop_only_allowed_in_planned_status():
    """Test que agregar parada solo está permitido en estado PLANNED"""
    route = Route.create(stops=[Stop(order_id="ORD001", priority=1)])
    
    route.start_route("VEH001")
    
    new_stop = Stop(order_id="ORD002", priority=2)
    
    with pytest.raises(ValueError, match="planificadas"):
        route.add_stop(new_stop)


def test_remove_stop_only_allowed_in_planned_status():
    """Test que remover parada solo está permitido en estado PLANNED"""
    route = Route.create(stops=[Stop(order_id="ORD001", priority=1)])
    
    route.start_route("VEH001")
    
    with pytest.raises(ValueError, match="planificadas"):
        route.remove_stop("ORD001")


def test_route_stops_sorted_by_priority():
    """Test que las paradas se ordenan por prioridad"""
    stops = [
        Stop(order_id="ORD003", priority=3),
        Stop(order_id="ORD001", priority=1),
        Stop(order_id="ORD002", priority=2)
    ]
    
    route = Route.create(stops=stops)
    
    # Debe estar ordenado por prioridad
    assert route.stops[0].order_id == "ORD001"
    assert route.stops[1].order_id == "ORD002"
    assert route.stops[2].order_id == "ORD003"


def test_add_stop_auto_sorts_by_priority():
    """Test que agregar parada ordena automáticamente"""
    route = Route.create(stops=[Stop(order_id="ORD003", priority=3)])
    
    route.add_stop(Stop(order_id="ORD001", priority=1))
    route.add_stop(Stop(order_id="ORD002", priority=2))
    
    # Debe estar ordenado
    assert route.stops[0].priority == 1
    assert route.stops[1].priority == 2
    assert route.stops[2].priority == 3


def test_route_requires_at_least_one_stop():
    """Test que la ruta siempre requiere al menos una parada"""
    route = Route.create(stops=[Stop(order_id="ORD001", priority=1)])
    
    # Intentar remover la última parada debe fallar
    with pytest.raises(ValueError, match="al menos una parada"):
        route.remove_stop("ORD001")


def test_cannot_complete_non_in_progress_route():
    """Test que no se puede completar ruta no en progreso"""
    route = Route.create(stops=[Stop(order_id="ORD001", priority=1)])
    
    # Intentar completar sin iniciar
    with pytest.raises(ValueError, match="en progreso"):
        route.complete_route()


def test_cannot_start_non_planned_route():
    """Test que no se puede iniciar ruta no planificada"""
    route = Route.create(stops=[Stop(order_id="ORD001", priority=1)])
    route.start_route("VEH001")
    
    # Intentar iniciar de nuevo
    with pytest.raises(ValueError, match="planificadas"):
        route.start_route("VEH002")


def test_cannot_cancel_completed_route():
    """Test que no se puede cancelar ruta completada"""
    route = Route.create(stops=[Stop(order_id="ORD001", priority=1)])
    route.start_route("VEH001")
    route.complete_route()
    
    # Intentar cancelar
    with pytest.raises(ValueError, match="completadas"):
        route.cancel_route()

