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
        status: RouteStatus = RouteStatus.PLANNED,
        route_number: Optional[str] = None,
        vendor_id: Optional[str] = None,
        vehicle_type: Optional[str] = None,
        driver_name: Optional[str] = None,
        driver_phone: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        estimated_distance: Optional[float] = None,
        estimated_duration: Optional[int] = None,  # en minutos
        estimated_fuel: Optional[float] = None,
        actual_distance: Optional[float] = None,
        actual_duration: Optional[int] = None,  # en minutos
        actual_fuel: Optional[float] = None,
        progress: Optional[float] = None  # porcentaje 0-100
    ):
        super().__init__(route_id)
        
        if not stops:
            raise ValueError("La ruta debe tener al menos una parada")
        
        self._stops = stops
        self._vehicle_id = vehicle_id
        self._status = status
        self._route_number = route_number or self._generate_route_number()
        self._vendor_id = vendor_id
        self._vehicle_type = vehicle_type
        self._driver_name = driver_name
        self._driver_phone = driver_phone
        self._start_time = start_time
        self._end_time = end_time
        self._estimated_distance = estimated_distance
        self._estimated_duration = estimated_duration
        self._estimated_fuel = estimated_fuel
        self._actual_distance = actual_distance
        self._actual_duration = actual_duration
        self._actual_fuel = actual_fuel
        self._progress = progress or 0.0
    
    def _generate_route_number(self) -> str:
        """Generar número de ruta único"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        import random
        random_part = random.randint(100, 999)
        return f"R-{timestamp}-{random_part}"
    
    @property
    def stops(self) -> List[Stop]:
        return self._stops
    
    @property
    def vehicle_id(self) -> Optional[str]:
        return self._vehicle_id
    
    @property
    def status(self) -> RouteStatus:
        return self._status
    
    @property
    def route_number(self) -> str:
        return self._route_number
    
    @property
    def vendor_id(self) -> Optional[str]:
        return self._vendor_id
    
    @property
    def vehicle_type(self) -> Optional[str]:
        return self._vehicle_type
    
    @property
    def driver_name(self) -> Optional[str]:
        return self._driver_name
    
    @property
    def driver_phone(self) -> Optional[str]:
        return self._driver_phone
    
    @property
    def start_time(self) -> Optional[datetime]:
        return self._start_time
    
    @property
    def end_time(self) -> Optional[datetime]:
        return self._end_time
    
    @property
    def estimated_distance(self) -> Optional[float]:
        return self._estimated_distance
    
    @property
    def estimated_duration(self) -> Optional[int]:
        return self._estimated_duration
    
    @property
    def estimated_fuel(self) -> Optional[float]:
        return self._estimated_fuel
    
    @property
    def actual_distance(self) -> Optional[float]:
        return self._actual_distance
    
    @property
    def actual_duration(self) -> Optional[int]:
        return self._actual_duration
    
    @property
    def actual_fuel(self) -> Optional[float]:
        return self._actual_fuel
    
    @property
    def progress(self) -> float:
        return self._progress
    
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
        self._start_time = datetime.utcnow()
        self._updated_at = datetime.utcnow()
    
    def complete_route(self):
        """Completar ruta"""
        if self._status != RouteStatus.IN_PROGRESS:
            raise ValueError("Solo se pueden completar rutas en progreso")
        
        self._status = RouteStatus.COMPLETED
        self._end_time = datetime.utcnow()
        self._progress = 100.0
        self._updated_at = datetime.utcnow()
    
    def update_progress(
        self,
        status: Optional[RouteStatus] = None,
        progress: Optional[float] = None,
        actual_distance: Optional[float] = None,
        actual_duration: Optional[int] = None,
        actual_fuel: Optional[float] = None,
        end_time: Optional[datetime] = None
    ):
        """Actualizar progreso de la ruta"""
        if status is not None:
            self._status = status
        if progress is not None:
            self._progress = max(0.0, min(100.0, progress))
        if actual_distance is not None:
            self._actual_distance = actual_distance
        if actual_duration is not None:
            self._actual_duration = actual_duration
        if actual_fuel is not None:
            self._actual_fuel = actual_fuel
        if end_time is not None:
            self._end_time = end_time
        self._updated_at = datetime.utcnow()
    
    def cancel_route(self):
        """Cancelar ruta"""
        if self._status == RouteStatus.COMPLETED:
            raise ValueError("No se pueden cancelar rutas completadas")
        
        self._status = RouteStatus.CANCELLED
        self._updated_at = datetime.utcnow()
    
    @staticmethod
    def create(
        stops: List[Stop], 
        vehicle_id: Optional[str] = None,
        route_number: Optional[str] = None,
        vendor_id: Optional[str] = None,
        vehicle_type: Optional[str] = None,
        driver_name: Optional[str] = None,
        driver_phone: Optional[str] = None,
        estimated_distance: Optional[float] = None,
        estimated_duration: Optional[int] = None,
        estimated_fuel: Optional[float] = None
    ) -> 'Route':
        """Factory method para crear una nueva ruta"""
        route = Route(
            route_id=EntityId(str(uuid4())),
            stops=stops,
            vehicle_id=vehicle_id,
            status=RouteStatus.PLANNED,
            route_number=route_number,
            vendor_id=vendor_id,
            vehicle_type=vehicle_type,
            driver_name=driver_name,
            driver_phone=driver_phone,
            estimated_distance=estimated_distance,
            estimated_duration=estimated_duration,
            estimated_fuel=estimated_fuel
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

