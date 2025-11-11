"""
Dependencies de la API
"""
from fastapi import Depends
from ...infrastructure.database import get_db
from ...infrastructure.repositories import SQLAlchemyLogisticsRepository
from ...domain.ports import ILogisticsRepository
from ...application.handlers import (
    CreateRouteCommandHandler,
    StartRouteCommandHandler,
    CompleteRouteCommandHandler,
    CancelRouteCommandHandler,
    GetRouteByIdQueryHandler,
    GetRoutesByVehicleQueryHandler,
    GetRoutesByStatusQueryHandler,
    GetAllRoutesQueryHandler
)


def get_logistics_repository(db=Depends(get_db)) -> ILogisticsRepository:
    """Dependency para obtener repositorio de logística"""
    return SQLAlchemyLogisticsRepository(db)


def get_create_route_handler(repo=Depends(get_logistics_repository)):
    """Dependency para obtener handler de crear ruta"""
    return CreateRouteCommandHandler(repo)


def get_start_route_handler(repo=Depends(get_logistics_repository)):
    """Dependency para obtener handler de iniciar ruta"""
    return StartRouteCommandHandler(repo)


def get_complete_route_handler(repo=Depends(get_logistics_repository)):
    """Dependency para obtener handler de completar ruta"""
    return CompleteRouteCommandHandler(repo)


def get_cancel_route_handler(repo=Depends(get_logistics_repository)):
    """Dependency para obtener handler de cancelar ruta"""
    return CancelRouteCommandHandler(repo)


def get_route_by_id_handler(repo=Depends(get_logistics_repository)):
    """Dependency para obtener handler de obtener ruta por ID"""
    return GetRouteByIdQueryHandler(repo)


def get_routes_by_vehicle_handler(repo=Depends(get_logistics_repository)):
    """Dependency para obtener handler de obtener rutas por vehículo"""
    return GetRoutesByVehicleQueryHandler(repo)


def get_routes_by_status_handler(repo=Depends(get_logistics_repository)):
    """Dependency para obtener handler de obtener rutas por estado"""
    return GetRoutesByStatusQueryHandler(repo)


def get_all_routes_handler(repo=Depends(get_logistics_repository)):
    """Dependency para obtener handler de obtener todas las rutas"""
    return GetAllRoutesQueryHandler(repo)

