"""
Entidad Notification del dominio de notificaciones
"""
from datetime import datetime
from typing import Optional
from enum import Enum
import sys
from pathlib import Path

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from shared.domain.entity import Entity
from shared.domain.value_objects import EntityId


class NotificationType(Enum):
    """Tipos de notificación"""
    ORDER = "order"
    SHIPMENT = "shipment"
    INVENTORY = "inventory"
    SYSTEM = "system"


class NotificationPriority(Enum):
    """Prioridad de notificación"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Notification(Entity):
    """Entidad que representa una notificación"""
    
    def __init__(
        self,
        notification_id: EntityId,
        user_id: EntityId,
        title: str,
        message: str,
        notification_type: NotificationType,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        is_read: bool = False,
        link: Optional[str] = None,
        metadata: Optional[dict] = None
    ):
        super().__init__(notification_id)
        self._user_id = user_id
        self._title = title
        self._message = message
        self._notification_type = notification_type
        self._priority = priority
        self._is_read = is_read
        self._link = link
        self._metadata = metadata or {}
    
    @property
    def user_id(self) -> EntityId:
        return self._user_id
    
    @property
    def title(self) -> str:
        return self._title
    
    @property
    def message(self) -> str:
        return self._message
    
    @property
    def notification_type(self) -> NotificationType:
        return self._notification_type
    
    @property
    def priority(self) -> NotificationPriority:
        return self._priority
    
    @property
    def is_read(self) -> bool:
        return self._is_read
    
    @property
    def link(self) -> Optional[str]:
        return self._link
    
    @property
    def metadata(self) -> dict:
        return self._metadata
    
    def mark_as_read(self):
        """Marcar notificación como leída"""
        if self._is_read:
            raise ValueError("La notificación ya está marcada como leída")
        
        self._is_read = True
        self._updated_at = datetime.utcnow()
    
    def mark_as_unread(self):
        """Marcar notificación como no leída"""
        if not self._is_read:
            raise ValueError("La notificación ya está sin leer")
        
        self._is_read = False
        self._updated_at = datetime.utcnow()
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at

