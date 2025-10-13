"""
Puertos (interfaces) del dominio de autenticación
"""
from abc import ABC, abstractmethod
from typing import Optional
import sys
from pathlib import Path

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from shared.domain.value_objects import EntityId, Email
from ..value_objects import Username
from ..entities import User


class IUserRepository(ABC):
    """Puerto (interfaz) para el repositorio de usuarios"""
    
    @abstractmethod
    async def save(self, user: User) -> User:
        """Guardar usuario"""
        pass
    
    @abstractmethod
    async def find_by_id(self, user_id: EntityId) -> Optional[User]:
        """Buscar usuario por ID"""
        pass
    
    @abstractmethod
    async def find_by_username(self, username: Username) -> Optional[User]:
        """Buscar usuario por username"""
        pass
    
    @abstractmethod
    async def find_by_email(self, email: Email) -> Optional[User]:
        """Buscar usuario por email"""
        pass
    
    @abstractmethod
    async def exists_by_username(self, username: Username) -> bool:
        """Verificar si existe un usuario con ese username"""
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: Email) -> bool:
        """Verificar si existe un usuario con ese email"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: EntityId) -> bool:
        """Eliminar usuario"""
        pass


class IPasswordHasher(ABC):
    """Puerto (interfaz) para el servicio de hash de contraseñas"""
    
    @abstractmethod
    def hash_password(self, plain_password: str) -> str:
        """Hashear contraseña"""
        pass
    
    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verificar contraseña"""
        pass


class ITokenService(ABC):
    """Puerto (interfaz) para el servicio de tokens JWT"""
    
    @abstractmethod
    def create_access_token(self, user_id: str, username: str, scopes: list) -> str:
        """Crear token de acceso"""
        pass
    
    @abstractmethod
    def create_refresh_token(self, user_id: str, username: str) -> str:
        """Crear token de refresco"""
        pass
    
    @abstractmethod
    def verify_access_token(self, token: str) -> dict:
        """Verificar token de acceso"""
        pass
    
    @abstractmethod
    def verify_refresh_token(self, token: str) -> dict:
        """Verificar token de refresco"""
        pass

