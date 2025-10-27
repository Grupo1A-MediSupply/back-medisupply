"""
Tests unitarios para comandos y queries
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from ...application.commands import (
    CreateRouteCommand, AddStopCommand, RemoveStopCommand,
    StartRouteCommand, CompleteRouteCommand, CancelRouteCommand
)
from ...application.queries import (
    GetRouteByIdQuery, GetRoutesByVehicleQuery, GetRoutesByStatusQuery,
    GetAllRoutesQuery
)


def test_create_route_command():
    """Test CreateRouteCommand"""
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
    command = StartRouteCommand(
        route_id="route-123",
        vehicle_id="VEH001"
    )
    
    assert command.route_id == "route-123"
    assert command.vehicle_id == "VEH001"


def test_complete_route_command():
    """Test CompleteRouteCommand"""
    command = CompleteRouteCommand(route_id="route-123")
    
    assert command.route_id == "route-123"


def test_cancel_route_command():
    """Test CancelRouteCommand"""
    command = CancelRouteCommand(route_id="route-123")
    
    assert command.route_id == "route-123"


def test_add_stop_command():
    """Test AddStopCommand"""
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
    command = RemoveStopCommand(
        route_id="route-123",
        order_id="ORD001"
    )
    
    assert command.route_id == "route-123"
    assert command.order_id == "ORD001"


def test_get_route_by_id_query():
    """Test GetRouteByIdQuery"""
    query = GetRouteByIdQuery(route_id="route-123")
    
    assert query.route_id == "route-123"


def test_get_routes_by_vehicle_query():
    """Test GetRoutesByVehicleQuery"""
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
    query = GetAllRoutesQuery(skip=10, limit=50)
    
    assert query.skip == 10
    assert query.limit == 50


def test_get_all_routes_query_defaults():
    """Test GetAllRoutesQuery con valores por defecto"""
    query = GetAllRoutesQuery()
    
    assert query.skip == 0
    assert query.limit == 100

