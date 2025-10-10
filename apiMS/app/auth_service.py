"""
Servicio de autenticación
"""
from datetime import datetime
from typing import Optional
import uuid
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .schemas import UserCreate, UserResponse, LoginRequest, Token, RefreshTokenRequest
from .models import User as UserModel
from .jwt_service import jwt_service

# Configuración de hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Servicio de autenticación"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verificar contraseña"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash de contraseña"""
        return pwd_context.hash(password)
    
    def get_user_by_username(self, username: str) -> Optional[UserModel]:
        """Obtener usuario por nombre de usuario"""
        return self.db.query(UserModel).filter(
            UserModel.username == username
        ).first()
    
    def get_user_by_email(self, email: str) -> Optional[UserModel]:
        """Obtener usuario por email"""
        return self.db.query(UserModel).filter(
            UserModel.email == email
        ).first()
    
    def get_user_by_id(self, user_id: str) -> Optional[UserModel]:
        """Obtener usuario por ID"""
        return self.db.query(UserModel).filter(
            UserModel.id == user_id
        ).first()
    
    def authenticate_user(self, username: str, password: str) -> Optional[UserModel]:
        """Autenticar usuario"""
        user = self.get_user_by_username(username)
        if not user:
            # Intentar con email
            user = self.get_user_by_email(username)
        
        if not user:
            return None
        
        if not self.verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        return user
    
    def create_user(self, user_data: UserCreate) -> UserModel:
        """Crear nuevo usuario"""
        # Verificar si el usuario ya existe
        if self.get_user_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está registrado"
            )
        
        if self.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        # Crear usuario
        hashed_password = self.get_password_hash(user_data.password)
        now = datetime.utcnow()
        
        user = UserModel(
            id=str(uuid.uuid4()),
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_active=user_data.is_active,
            is_superuser=user_data.is_superuser,
            created_at=now,
            updated_at=now
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def login(self, login_data: LoginRequest) -> Token:
        """Iniciar sesión"""
        user = self.authenticate_user(login_data.username, login_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Crear tokens
        access_token = jwt_service.create_access_token(
            data={
                "sub": user.username, 
                "user_id": str(user.id), 
                "scopes": ["read", "write"]
            }
        )
        
        refresh_token = jwt_service.create_refresh_token(
            data={"sub": user.username, "user_id": str(user.id)}
        )
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=jwt_service.access_token_expire_minutes * 60
        )
    
    def refresh_token(self, refresh_data: RefreshTokenRequest) -> Token:
        """Refrescar token"""
        try:
            payload = jwt_service.verify_refresh_token(refresh_data.refresh_token)
            username = payload.get("sub")
            user_id = payload.get("user_id")
            
            if not username or not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token de refresco inválido"
                )
            
            user = self.get_user_by_id(user_id)
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no encontrado o inactivo"
                )
            
            # Crear nuevos tokens
            access_token = jwt_service.create_access_token(
                data={
                    "sub": user.username, 
                    "user_id": str(user.id), 
                    "scopes": ["read", "write"]
                }
            )
            
            new_refresh_token = jwt_service.create_refresh_token(
                data={"sub": user.username, "user_id": str(user.id)}
            )
            
            return Token(
                access_token=access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                expires_in=jwt_service.access_token_expire_minutes * 60
            )
            
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de refresco inválido"
            )
    
    def get_current_user(self, token: str) -> UserModel:
        """Obtener usuario actual desde token"""
        try:
            payload = jwt_service.verify_access_token(token)
            username = payload.get("sub")
            user_id = payload.get("user_id")
            
            if not username or not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido"
                )
            
            user = self.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no encontrado"
                )
            
            return user
            
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )

