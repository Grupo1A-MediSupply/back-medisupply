"""
Eventos de dominio base
"""
from abc import ABC
from datetime import datetime
from typing import Any, Dict
from uuid import uuid4


class DomainEvent(ABC):
    """Clase base para eventos de dominio"""
    
    def __init__(self):
        self.event_id: str = str(uuid4())
        self.occurred_at: datetime = datetime.utcnow()
        self.aggregate_id: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir evento a diccionario"""
        return {
            "event_id": self.event_id,
            "event_type": self.__class__.__name__,
            "occurred_at": self.occurred_at.isoformat(),
            "aggregate_id": self.aggregate_id,
            "data": self._event_data()
        }
    
    def _event_data(self) -> Dict[str, Any]:
        """Datos específicos del evento (sobrescribir en subclases)"""
        return {}


class EventBus:
    """Bus de eventos para publicar y suscribirse a eventos"""
    
    def __init__(self):
        self._handlers: Dict[str, list] = {}
    
    def subscribe(self, event_type: str, handler):
        """Suscribirse a un tipo de evento"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    async def publish(self, event: DomainEvent):
        """Publicar un evento"""
        event_type = event.__class__.__name__
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                await handler(event)
    
    def clear(self):
        """Limpiar todos los handlers"""
        self._handlers.clear()


# Instancia global del event bus
event_bus = EventBus()

