"""
Comandos del servicio de logística
"""
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class CreateRouteCommand:
    """Comando para crear una ruta"""
    stops: List[dict]  # [{"orderId": str, "priority": int, "eta": dict}]
    vehicle_id: Optional[str] = None
    vendor_id: Optional[str] = None
    vehicle_type: Optional[str] = None
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    estimated_distance: Optional[float] = None
    estimated_duration: Optional[int] = None
    estimated_fuel: Optional[float] = None


@dataclass
class AddStopCommand:
    """Comando para agregar parada a una ruta"""
    route_id: str
    order_id: str
    priority: int = 1
    eta: Optional[dict] = None


@dataclass
class RemoveStopCommand:
    """Comando para eliminar parada de una ruta"""
    route_id: str
    order_id: str


@dataclass
class StartRouteCommand:
    """Comando para iniciar una ruta"""
    route_id: str
    vehicle_id: str


@dataclass
class CompleteRouteCommand:
    """Comando para completar una ruta"""
    route_id: str


@dataclass
class CancelRouteCommand:
    """Comando para cancelar una ruta"""
    route_id: str


@dataclass
class UpdateTrackingCommand:
    """Comando para actualizar seguimiento"""
    route_id: str
    position: dict  # {"lat": float, "lon": float}
    next_stop_eta: Optional[dict] = None


@dataclass
class UpdateRouteCommand:
    """Comando para actualizar una ruta"""
    route_id: str
    status: Optional[str] = None
    progress: Optional[float] = None
    actual_distance: Optional[float] = None
    actual_duration: Optional[int] = None
    actual_fuel: Optional[float] = None
    end_time: Optional[datetime] = None


@dataclass
class DeleteRouteCommand:
    """Comando para eliminar una ruta"""
    route_id: str


@dataclass
class GenerateOptimalRouteCommand:
    """Comando para generar ruta óptima"""
    order_ids: List[str]
    vehicle_type: Optional[str] = None

