"""
Repositorios de infraestructura - Versión corregida
"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, Boolean, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
import sys
from pathlib import Path

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)
    print(f"Added shared path: {shared_path}")

# Agregar el directorio del auth-service al PYTHONPATH
auth_service_path = str(Path(__file__).parent.parent.parent)
if auth_service_path not in sys.path:
    sys.path.insert(0, auth_service_path)

from shared.domain.value_objects import EntityId, Email
try:
    from ...domain.entities import User
    from ...domain.value_objects import Username, HashedPassword, FullName, PhoneNumber
    from ...domain.ports import IUserRepository
except ImportError:
    from domain.entities import User
    from domain.value_objects import Username, HashedPassword, FullName, PhoneNumber
    from domain.ports import IUserRepository

Base = declarative_base()


class UserModel(Base):
    """Modelo de base de datos para User"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)


class VerificationCodeModel(Base):
    """Modelo de base de datos para códigos de verificación"""
    __tablename__ = "verification_codes"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    code = Column(String, nullable=False)
    email = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False)


class SQLAlchemyUserRepository(IUserRepository):
    """Repositorio de usuarios con SQLAlchemy"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _to_domain(self, model: UserModel) -> User:
        """Convertir modelo de DB a entidad de dominio"""
        return User(
            user_id=EntityId(model.id),
            email=Email(model.email),
            username=Username(model.username),
            hashed_password=HashedPassword(model.hashed_password),
            full_name=FullName(model.full_name) if model.full_name else None,
            phone_number=PhoneNumber(model.phone_number) if model.phone_number else None,
            is_active=model.is_active,
            is_superuser=model.is_superuser
        )
    
    def _to_model(self, user: User) -> UserModel:
        """Convertir entidad de dominio a modelo de DB"""
        return UserModel(
            id=str(user.id),
            email=str(user.email),
            username=str(user.username),
            hashed_password=str(user.hashed_password),
            full_name=str(user.full_name) if user.full_name else None,
            phone_number=str(user.phone_number) if user.phone_number else None,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    
    async def save(self, user: User) -> User:
        """Guardar usuario"""
        # Buscar si existe
        existing = self.db.query(UserModel).filter(
            UserModel.id == str(user.id)
        ).first()
        
        if existing:
            # Actualizar
            existing.email = str(user.email)
            existing.username = str(user.username)
            existing.hashed_password = str(user.hashed_password)
            existing.full_name = str(user.full_name) if user.full_name else None
            existing.phone_number = str(user.phone_number) if user.phone_number else None
            existing.is_active = user.is_active
            existing.is_superuser = user.is_superuser
            existing.updated_at = user.updated_at
        else:
            # Crear nuevo
            model = self._to_model(user)
            self.db.add(model)
        
        self.db.commit()
        
        # Refrescar
        model = self.db.query(UserModel).filter(
            UserModel.id == str(user.id)
        ).first()
        
        return self._to_domain(model)
    
    async def find_by_id(self, user_id: EntityId) -> Optional[User]:
        """Buscar usuario por ID"""
        model = self.db.query(UserModel).filter(
            UserModel.id == str(user_id)
        ).first()
        
        return self._to_domain(model) if model else None
    
    async def find_by_username(self, username: Username) -> Optional[User]:
        """Buscar usuario por username"""
        model = self.db.query(UserModel).filter(
            UserModel.username == str(username)
        ).first()
        
        return self._to_domain(model) if model else None
    
    async def find_by_email(self, email: Email) -> Optional[User]:
        """Buscar usuario por email"""
        model = self.db.query(UserModel).filter(
            UserModel.email == str(email)
        ).first()
        
        return self._to_domain(model) if model else None
    
    async def exists_by_username(self, username: Username) -> bool:
        """Verificar si existe usuario con ese username"""
        count = self.db.query(UserModel).filter(
            UserModel.username == str(username)
        ).count()
        
        return count > 0
    
    async def exists_by_email(self, email: Email) -> bool:
        """Verificar si existe usuario con ese email"""
        count = self.db.query(UserModel).filter(
            UserModel.email == str(email)
        ).count()
        
        return count > 0
    
    async def delete(self, user_id: EntityId) -> bool:
        """Eliminar usuario"""
        model = self.db.query(UserModel).filter(
            UserModel.id == str(user_id)
        ).first()
        
        if model:
            self.db.delete(model)
            self.db.commit()
            return True
        
        return False
