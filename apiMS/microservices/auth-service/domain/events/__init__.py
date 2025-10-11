"""
Eventos de dominio del servicio de autenticación
"""
from typing import Dict, Any
import sys
from pathlib import Path

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from shared.domain.events import DomainEvent


class UserRegisteredEvent(DomainEvent):
    """Evento que se dispara cuando un usuario se registra"""
    
    def __init__(self, user_id: str, username: str, email: str):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.email = email
        self.aggregate_id = user_id
    
    def _event_data(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email
        }


class UserLoggedInEvent(DomainEvent):
    """Evento que se dispara cuando un usuario inicia sesión"""
    
    def __init__(self, user_id: str, username: str):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.aggregate_id = user_id
    
    def _event_data(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "username": self.username
        }


class TokenRefreshedEvent(DomainEvent):
    """Evento que se dispara cuando se refresca un token"""
    
    def __init__(self, user_id: str):
        super().__init__()
        self.user_id = user_id
        self.aggregate_id = user_id
    
    def _event_data(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id
        }


class UserDeactivatedEvent(DomainEvent):
    """Evento que se dispara cuando un usuario es desactivado"""
    
    def __init__(self, user_id: str):
        super().__init__()
        self.user_id = user_id
        self.aggregate_id = user_id
    
    def _event_data(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id
        }

