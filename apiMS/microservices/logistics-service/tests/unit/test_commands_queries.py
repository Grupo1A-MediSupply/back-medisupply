"""
Tests unitarios para comandos y queries
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime

# Agregar paths al PYTHONPATH
logistics_service_path = str(Path(__file__).parent.parent.parent.resolve())
shared_path = str(Path(__file__).parent.parent.parent.parent.resolve() / "shared")
if logistics_service_path not in sys.path:
    sys.path.insert(0, logistics_service_path)
if shared_path not in sys.path:
    sys.path.insert(0, str(shared_path))

# Los imports se hacen dentro de las funciones para evitar problemas cuando pytest carga el módulo


def test_create_route_command():
    """Test CreateRouteCommand"""
    from application.commands import CreateRouteCommand
    command = CreateRouteCommand(
        stops=[
            {"orderId": "ORD001", "priority": 1},
            {"orderId": "ORD002", "priority": 2}
        ],
        vehicle_id="VEH001"
    )
    
    assert len(command.stops) == 2
    assert command.vehicle_id == "VEH001"


def test_start_route_command():
    """Test StartRouteCommand"""
    from application.commands import StartRouteCommand
    command = StartRouteCommand(
        route_id="route-123",
        vehicle_id="VEH001"
    )
    
    assert command.route_id == "route-123"
    assert command.vehicle_id == "VEH001"


def test_complete_route_command():
    """Test CompleteRouteCommand"""
    from application.commands import CompleteRouteCommand
    command = CompleteRouteCommand(route_id="route-123")
    
    assert command.route_id == "route-123"


def test_cancel_route_command():
    """Test CancelRouteCommand"""
    from application.commands import CancelRouteCommand
    command = CancelRouteCommand(route_id="route-123")
    
    assert command.route_id == "route-123"


def test_add_stop_command():
    """Test AddStopCommand"""
    from application.commands import AddStopCommand
    command = AddStopCommand(
        route_id="route-123",
        order_id="ORD001",
        priority=1
    )
    
    assert command.route_id == "route-123"
    assert command.order_id == "ORD001"
    assert command.priority == 1


def test_remove_stop_command():
    """Test RemoveStopCommand"""
    from application.commands import RemoveStopCommand
    command = RemoveStopCommand(
        route_id="route-123",
        order_id="ORD001"
    )
    
    assert command.route_id == "route-123"
    assert command.order_id == "ORD001"


def test_get_route_by_id_query():
    """Test GetRouteByIdQuery"""
    from application.queries import GetRouteByIdQuery
    query = GetRouteByIdQuery(route_id="route-123")
    
    assert query.route_id == "route-123"


def test_get_routes_by_vehicle_query():
    """Test GetRoutesByVehicleQuery"""
    from application.queries import GetRoutesByVehicleQuery
    query = GetRoutesByVehicleQuery(
        vehicle_id="VEH001",
        skip=0,
        limit=10
    )
    
    assert query.vehicle_id == "VEH001"
    assert query.skip == 0
    assert query.limit == 10


def test_get_routes_by_status_query():
    """Test GetRoutesByStatusQuery"""
    from application.queries import GetRoutesByStatusQuery
    query = GetRoutesByStatusQuery(
        status="IN_PROGRESS",
        skip=0,
        limit=10
    )
    
    assert query.status == "IN_PROGRESS"
    assert query.skip == 0
    assert query.limit == 10


def test_get_all_routes_query():
    """Test GetAllRoutesQuery"""
    from application.queries import GetAllRoutesQuery
    query = GetAllRoutesQuery(skip=10, limit=50)
    
    assert query.skip == 10
    assert query.limit == 50


def test_get_all_routes_query_defaults():
    """Test GetAllRoutesQuery con valores por defecto"""
    from application.queries import GetAllRoutesQuery
    query = GetAllRoutesQuery()
    
    assert query.skip == 0
    assert query.limit == 100

