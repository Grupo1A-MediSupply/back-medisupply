"""
Queries del servicio de logística
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class GetRouteByIdQuery:
    """Query para obtener una ruta por ID"""
    route_id: str


@dataclass
class GetRoutesByVehicleQuery:
    """Query para obtener rutas por vehículo"""
    vehicle_id: str
    skip: int = 0
    limit: int = 100


@dataclass
class GetRoutesByStatusQuery:
    """Query para obtener rutas por estado"""
    status: str
    skip: int = 0
    limit: int = 100


@dataclass
class GetTrackingInfoQuery:
    """Query para obtener información de seguimiento"""
    route_id: str


@dataclass
class GetAllRoutesQuery:
    """Query para obtener todas las rutas"""
    skip: int = 0
    limit: int = 100
    status: Optional[str] = None

