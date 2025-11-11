"""
Entidades del dominio de logística
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import uuid4, UUID
import sys
from pathlib import Path

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from shared.domain.entity import Entity
from shared.domain.value_objects import EntityId


class RouteStatus(Enum):
    """Estados de una ruta"""
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Position:
    """Value Object para posición GPS"""
    
    def __init__(self, lat: float, lon: float, timestamp: datetime):
        if not (-90 <= lat <= 90):
            raise ValueError("Latitud debe estar entre -90 y 90")
        if not (-180 <= lon <= 180):
            raise ValueError("Longitud debe estar entre -180 y 180")
        
        self.lat = lat
        self.lon = lon
        self.ts = timestamp
    
    def to_dict(self) -> dict:
        """Convertir a diccionario"""
        return {
            "lat": self.lat,
            "lon": self.lon,
            "ts": self.ts.isoformat()
        }


class ETA:
    """Value Object para tiempo estimado de llegada"""
    
    def __init__(self, date: datetime, window_minutes: int):
        if window_minutes < 0:
            raise ValueError("La ventana de tiempo no puede ser negativa")
        
        self.date = date
        self.window_minutes = window_minutes
    
    def to_dict(self) -> dict:
        """Convertir a diccionario"""
        return {
            "date": self.date.isoformat(),
            "windowMinutes": self.window_minutes
        }


class Stop:
    """Value Object para parada de ruta"""
    
    def __init__(self, order_id: str, eta: Optional[ETA] = None, priority: int = 1):
        if not order_id or not order_id.strip():
            raise ValueError("Order ID es requerido")
        if priority < 1:
            raise ValueError("La prioridad debe ser mayor a 0")
        
        self.order_id = order_id
        self.eta = eta
        self.priority = priority
    
    def to_dict(self) -> dict:
        """Convertir a diccionario"""
        result = {
            "orderId": self.order_id,
            "priority": self.priority
        }
        if self.eta:
            result["eta"] = self.eta.to_dict()
        return result


class Route(Entity):
    """Entidad Route del dominio de logística"""
    
    def __init__(
        self,
        route_id: EntityId,
        stops: List[Stop],
        vehicle_id: Optional[str] = None,
        status: RouteStatus = RouteStatus.PLANNED
    ):
        super().__init__(route_id)
        
        if not stops:
            raise ValueError("La ruta debe tener al menos una parada")
        
        self._stops = stops
        self._vehicle_id = vehicle_id
        self._status = status
    
    @property
    def stops(self) -> List[Stop]:
        return self._stops
    
    @property
    def vehicle_id(self) -> Optional[str]:
        return self._vehicle_id
    
    @property
    def status(self) -> RouteStatus:
        return self._status
    
    def add_stop(self, stop: Stop):
        """Agregar parada a la ruta"""
        if self._status != RouteStatus.PLANNED:
            raise ValueError("Solo se pueden agregar paradas a rutas planificadas")
        
        self._stops.append(stop)
        self._stops.sort(key=lambda s: s.priority)
        self._updated_at = datetime.utcnow()
    
    def remove_stop(self, order_id: str):
        """Eliminar parada de la ruta"""
        if self._status != RouteStatus.PLANNED:
            raise ValueError("Solo se pueden eliminar paradas de rutas planificadas")
        
        stop = next((s for s in self._stops if s.order_id == order_id), None)
        if not stop:
            raise ValueError(f"Parada con order_id {order_id} no encontrada")
        
        self._stops.remove(stop)
        if not self._stops:
            raise ValueError("La ruta debe tener al menos una parada")
        
        self._updated_at = datetime.utcnow()
    
    def start_route(self, vehicle_id: str):
        """Iniciar ruta"""
        if self._status != RouteStatus.PLANNED:
            raise ValueError("Solo se pueden iniciar rutas planificadas")
        
        self._status = RouteStatus.IN_PROGRESS
        self._vehicle_id = vehicle_id
        self._updated_at = datetime.utcnow()
    
    def complete_route(self):
        """Completar ruta"""
        if self._status != RouteStatus.IN_PROGRESS:
            raise ValueError("Solo se pueden completar rutas en progreso")
        
        self._status = RouteStatus.COMPLETED
        self._updated_at = datetime.utcnow()
    
    def cancel_route(self):
        """Cancelar ruta"""
        if self._status == RouteStatus.COMPLETED:
            raise ValueError("No se pueden cancelar rutas completadas")
        
        self._status = RouteStatus.CANCELLED
        self._updated_at = datetime.utcnow()
    
    @staticmethod
    def create(stops: List[Stop], vehicle_id: Optional[str] = None) -> 'Route':
        """Factory method para crear una nueva ruta"""
        route = Route(
            route_id=EntityId(str(uuid4())),
            stops=stops,
            vehicle_id=vehicle_id,
            status=RouteStatus.PLANNED
        )
        
        return route


class TrackingInfo:
    """Value Object para información de seguimiento"""
    
    def __init__(
        self,
        vehicle_id: str,
        position: Optional[Position] = None,
        next_stop_eta: Optional[ETA] = None
    ):
        if not vehicle_id or not vehicle_id.strip():
            raise ValueError("Vehicle ID es requerido")
        
        self.vehicle_id = vehicle_id
        self.position = position
        self.next_stop_eta = next_stop_eta
    
    def to_dict(self) -> dict:
        """Convertir a diccionario"""
        result = {"vehicleId": self.vehicle_id}
        
        if self.position:
            result["position"] = self.position.to_dict()
        
        if self.next_stop_eta:
            result["nextStopEta"] = self.next_stop_eta.to_dict()
        
        return result

