"""
Servicios de aplicación para logística
"""
import sys
from pathlib import Path

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from shared.domain.events import event_bus
from ...domain.events import (
    RouteCreatedEvent, RouteStartedEvent, RouteCompletedEvent, RouteCancelledEvent
)


class LogisticsEventHandler:
    """Event Handler para eventos de logística"""
    
    async def handle_route_created(self, event: RouteCreatedEvent):
        """Manejar evento de ruta creada"""
        print(f"🗺️ Nueva ruta creada: {event.route_id}")
    
    async def handle_route_started(self, event: RouteStartedEvent):
        """Manejar evento de ruta iniciada"""
        print(f"🚀 Ruta iniciada: {event.route_id} con vehículo {event.vehicle_id}")
    
    async def handle_route_completed(self, event: RouteCompletedEvent):
        """Manejar evento de ruta completada"""
        print(f"✅ Ruta completada: {event.route_id}")
    
    async def handle_route_cancelled(self, event: RouteCancelledEvent):
        """Manejar evento de ruta cancelada"""
        print(f"❌ Ruta cancelada: {event.route_id}")


def setup_event_handlers(event_handler: LogisticsEventHandler):
    """Configurar event handlers"""
    event_bus.subscribe(RouteCreatedEvent, event_handler.handle_route_created)
    event_bus.subscribe(RouteStartedEvent, event_handler.handle_route_started)
    event_bus.subscribe(RouteCompletedEvent, event_handler.handle_route_completed)
    event_bus.subscribe(RouteCancelledEvent, event_handler.handle_route_cancelled)

