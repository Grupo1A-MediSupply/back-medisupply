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

