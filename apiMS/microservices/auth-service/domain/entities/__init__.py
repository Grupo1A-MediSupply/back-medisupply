"""
Entidades del dominio de autenticación
"""
from datetime import datetime
from typing import Optional
import sys
from pathlib import Path

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from shared.domain.entity import Entity
from shared.domain.value_objects import EntityId, Email
from ..value_objects import Username, HashedPassword, FullName, PhoneNumber
from ..events import UserRegisteredEvent, UserLoggedInEvent, UserDeactivatedEvent


class User(Entity):
    """Entidad User del dominio de autenticación"""
    
    def __init__(
        self,
        user_id: EntityId,
        email: Email,
        username: Username,
        hashed_password: HashedPassword,
        full_name: Optional[FullName] = None,
        phone_number: Optional[PhoneNumber] = None,
        is_active: bool = True,
        is_superuser: bool = False
    ):
        super().__init__(user_id)
        self._email = email
        self._username = username
        self._hashed_password = hashed_password
        self._full_name = full_name
        self._phone_number = phone_number
        self._is_active = is_active
        self._is_superuser = is_superuser
    
    @property
    def email(self) -> Email:
        return self._email
    
    @property
    def username(self) -> Username:
        return self._username
    
    @property
    def hashed_password(self) -> HashedPassword:
        return self._hashed_password
    
    @property
    def full_name(self) -> Optional[FullName]:
        return self._full_name
    
    @property
    def phone_number(self) -> Optional[PhoneNumber]:
        return self._phone_number
    
    @property
    def is_active(self) -> bool:
        return self._is_active
    
    @property
    def is_superuser(self) -> bool:
        return self._is_superuser
    
    def change_password(self, new_hashed_password: HashedPassword):
        """Cambiar contraseña del usuario"""
        self._hashed_password = new_hashed_password
        self._updated_at = datetime.utcnow()
    
    def deactivate(self):
        """Desactivar usuario"""
        if not self._is_active:
            raise ValueError("El usuario ya está desactivado")
        
        self._is_active = False
        self._updated_at = datetime.utcnow()
        self._record_event(UserDeactivatedEvent(str(self._id)))
    
    def activate(self):
        """Activar usuario"""
        if self._is_active:
            raise ValueError("El usuario ya está activo")
        
        self._is_active = True
        self._updated_at = datetime.utcnow()
    
    def update_profile(self, full_name: Optional[FullName] = None, phone_number: Optional[PhoneNumber] = None):
        """Actualizar perfil del usuario"""
        if full_name:
            self._full_name = full_name
        if phone_number:
            self._phone_number = phone_number
        self._updated_at = datetime.utcnow()
    
    @staticmethod
    def register(
        user_id: EntityId,
        email: Email,
        username: Username,
        hashed_password: HashedPassword,
        full_name: Optional[FullName] = None,
        phone_number: Optional[PhoneNumber] = None,
        is_active: bool = True,
        is_superuser: bool = False
    ) -> 'User':
        """Factory method para registrar un nuevo usuario"""
        user = User(
            user_id=user_id,
            email=email,
            username=username,
            hashed_password=hashed_password,
            full_name=full_name,
            phone_number=phone_number,
            is_active=is_active,
            is_superuser=is_superuser
        )
        
        # Registrar evento de dominio
        user._record_event(UserRegisteredEvent(
            user_id=str(user_id),
            username=str(username),
            email=str(email)
        ))
        
        return user
    
    def login(self):
        """Registrar evento de login"""
        if not self._is_active:
            raise ValueError("El usuario está desactivado")
        
        self._record_event(UserLoggedInEvent(
            user_id=str(self._id),
            username=str(self._username)
        ))

