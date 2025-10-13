"""
Event handlers del servicio de autenticación
"""
import sys
from pathlib import Path

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from shared.domain.events import DomainEvent
from ...domain.events import UserRegisteredEvent, UserLoggedInEvent, UserDeactivatedEvent


class UserEventHandler:
    """Handler para eventos de usuario"""
    
    async def on_user_registered(self, event: UserRegisteredEvent):
        """Manejar evento de usuario registrado"""
        print(f"📧 [EVENT] Usuario registrado: {event.username} ({event.email})")
        # Aquí se podría enviar un email de bienvenida
        # Aquí se podría publicar a un message broker (RabbitMQ, Kafka, etc.)
    
    async def on_user_logged_in(self, event: UserLoggedInEvent):
        """Manejar evento de usuario logueado"""
        print(f"🔐 [EVENT] Usuario logueado: {event.username}")
        # Aquí se podría registrar en un sistema de analytics
        # Aquí se podría actualizar la fecha de último login
    
    async def on_user_deactivated(self, event: UserDeactivatedEvent):
        """Manejar evento de usuario desactivado"""
        print(f"❌ [EVENT] Usuario desactivado: {event.user_id}")
        # Aquí se podría invalidar todas las sesiones del usuario
        # Aquí se podría notificar a otros servicios


def setup_event_handlers(event_handler: UserEventHandler):
    """Configurar handlers de eventos"""
    from shared.domain.events import event_bus
    
    event_bus.subscribe("UserRegisteredEvent", event_handler.on_user_registered)
    event_bus.subscribe("UserLoggedInEvent", event_handler.on_user_logged_in)
    event_bus.subscribe("UserDeactivatedEvent", event_handler.on_user_deactivated)

