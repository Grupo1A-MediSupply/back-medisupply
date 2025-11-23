"""
Entidad base del dominio
"""
from abc import ABC
from datetime import datetime
from typing import List
from .events import DomainEvent
from .value_objects import EntityId


class Entity(ABC):
    """Clase base para entidades de dominio"""
    
    def __init__(self, entity_id: EntityId):
        self._id = entity_id
        self._domain_events: List[DomainEvent] = []
        self._created_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()
    
    @property
    def id(self) -> EntityId:
        return self._id
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    def _record_event(self, event: DomainEvent):
        """Registrar un evento de dominio"""
        event.aggregate_id = str(self._id)
        self._domain_events.append(event)
    
    def get_domain_events(self) -> List[DomainEvent]:
        """Obtener eventos de dominio"""
        return self._domain_events.copy()
    
    def clear_domain_events(self):
        """Limpiar eventos de dominio"""
        self._domain_events.clear()
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Entity):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        return hash(self._id)

