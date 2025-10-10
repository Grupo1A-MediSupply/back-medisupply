"""
Esquemas Pydantic para validación de datos
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr


# ========== Esquemas de Usuario ==========

class UserBase(BaseModel):
    """Modelo base de usuario"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    """Modelo para crear usuario"""
    password: str = Field(..., min_length=8, description="Contraseña mínima 8 caracteres")


class UserUpdate(BaseModel):
    """Modelo para actualizar usuario"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)


class UserResponse(BaseModel):
    """Respuesta de usuario"""
    id: str
    email: str
    username: str
    full_name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserInDB(UserBase):
    """Modelo de usuario en base de datos"""
    id: UUID
    hashed_password: str
    created_at: datetime
    updated_at: datetime


# ========== Esquemas de Autenticación ==========

class LoginRequest(BaseModel):
    """Solicitud de login"""
    username: str = Field(..., description="Nombre de usuario o email")
    password: str = Field(..., description="Contraseña")


class Token(BaseModel):
    """Modelo de token"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Solicitud de refresh token"""
    refresh_token: str = Field(..., description="Token de refresco")


class TokenVerifyResponse(BaseModel):
    """Respuesta de verificación de token"""
    valid: bool
    user: Optional[dict] = None
    error: Optional[str] = None


class LogoutResponse(BaseModel):
    """Respuesta de logout"""
    message: str


# ========== Esquemas de Producto ==========

class ProductBase(BaseModel):
    """Modelo base de producto"""
    name: str = Field(..., min_length=1, max_length=255, description="Nombre del producto")
    description: Optional[str] = Field(None, description="Descripción del producto")
    price: float = Field(..., gt=0, description="Precio del producto (debe ser mayor a 0)")
    stock: int = Field(default=0, ge=0, description="Stock disponible")
    is_active: bool = Field(default=True, description="Si el producto está activo")


class ProductCreate(ProductBase):
    """Modelo para crear producto"""
    pass


class ProductUpdate(BaseModel):
    """Modelo para actualizar producto"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    """Respuesta de producto"""
    id: str
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

