"""
Eventos de dominio para logística
"""
import sys
from pathlib import Path

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from shared.domain.events import DomainEvent


class RouteCreatedEvent(DomainEvent):
    """Evento cuando se crea una ruta"""
    
    def __init__(self, route_id: str, vehicle_id: str = None):
        super().__init__()
        self.route_id = route_id
        self.vehicle_id = vehicle_id


class RouteStartedEvent(DomainEvent):
    """Evento cuando se inicia una ruta"""
    
    def __init__(self, route_id: str, vehicle_id: str):
        super().__init__()
        self.route_id = route_id
        self.vehicle_id = vehicle_id


class RouteCompletedEvent(DomainEvent):
    """Evento cuando se completa una ruta"""
    
    def __init__(self, route_id: str):
        super().__init__()
        self.route_id = route_id


class RouteCancelledEvent(DomainEvent):
    """Evento cuando se cancela una ruta"""
    
    def __init__(self, route_id: str):
        super().__init__()
        self.route_id = route_id

