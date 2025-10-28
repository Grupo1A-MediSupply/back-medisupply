"""
Rutas de la API de autenticación
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
import sys
from pathlib import Path

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from ...application.commands import (
    RegisterUserCommand,
    LoginCommand,
    RefreshTokenCommand,
    ChangePasswordCommand,
    DeactivateUserCommand,
    UpdateProfileCommand,
    VerifyCodeCommand,
    ResendCodeCommand
)
from ...application.queries import (
    GetUserByIdQuery,
    GetCurrentUserQuery,
    VerifyTokenQuery
)
from ..dependencies import (
    get_register_user_handler,
    get_login_handler,
    get_refresh_token_handler,
    get_change_password_handler,
    get_deactivate_user_handler,
    get_update_profile_handler,
    get_user_by_id_handler,
    get_current_user_handler,
    get_verify_token_handler
)

router = APIRouter()
security = HTTPBearer()


# ========== Schemas ==========

class RegisterRequest(BaseModel):
    """Request para registro de usuario"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    confirm_password: Optional[str] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False


class LoginRequest(BaseModel):
    """Request para login"""
    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    """Request para refresh token"""
    refresh_token: str


class TokenResponse(BaseModel):
    """Response de token"""
    access_token: str
    refresh_token: str
    token_type: str


class UserResponse(BaseModel):
    """Response de usuario"""
    id: str
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime


class VerifyTokenResponse(BaseModel):
    """Response de verificación de token"""
    valid: bool
    user: Optional[dict] = None
    error: Optional[str] = None


class MessageResponse(BaseModel):
    """Response de mensaje"""
    message: str


class VerifyCodeRequest(BaseModel):
    """Request para verificar código"""
    user_id: str
    code: str


class ResendCodeRequest(BaseModel):
    """Request para reenviar código"""
    user_id: str


class ChangePasswordRequest(BaseModel):
    """Request para cambiar contraseña"""
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_new_password: str


# ========== Endpoints ==========

@router.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar usuario",
    description="Registra un nuevo usuario en el sistema"
)
async def register(
    request: RegisterRequest,
    handler=Depends(get_register_user_handler)
):
    """Registrar nuevo usuario"""
    try:
        # Verificar que las contraseñas coincidan
        if request.confirm_password and request.password != request.confirm_password:
            raise ValueError("Las contraseñas no coinciden")
        
        command = RegisterUserCommand(
            email=request.email,
            username=request.username,
            password=request.password,
            confirm_password=request.confirm_password,
            full_name=request.full_name,
            phone_number=request.phone_number,
            is_active=request.is_active,
            is_superuser=request.is_superuser
        )
        
        user = await handler.handle(command)
        
        return {
            "success": True,
            "user_id": str(user.id),
            "message": "Usuario registrado exitosamente"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post(
    "/auth/login",
    response_model=dict,
    summary="Iniciar sesión",
    description="Inicia sesión y devuelve user_id para verificación"
)
async def login(
    request: LoginRequest,
    handler=Depends(get_login_handler)
):
    """Iniciar sesión y obtener tokens"""
    try:
        command = LoginCommand(
            username=request.username,
            password=request.password
        )
        
        result = await handler.handle(command)
        
        # Devolver user_id según el contrato de Postman
        return {
            "user_id": result.get("user_id", ""),
            "message": "Inicio de sesión exitoso"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post(
    "/auth/verify-code",
    response_model=dict,
    summary="Verificar código",
    description="Verifica el código de verificación y devuelve tokens"
)
async def verify_code(
    request: VerifyCodeRequest
):
    """Verificar código de verificación"""
    try:
        # TODO: Implementar lógica de verificación de código
        # Por ahora, simular verificación exitosa
        return {
            "access_token": "mock_access_token",
            "refresh_token": "mock_refresh_token",
            "token_type": "Bearer"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/auth/resend-code",
    response_model=MessageResponse,
    summary="Reenviar código",
    description="Reenvía el código de verificación"
)
async def resend_code(
    request: ResendCodeRequest
):
    """Reenviar código de verificación"""
    try:
        # TODO: Implementar lógica de reenvío de código
        return MessageResponse(message="Código reenviado exitosamente")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/auth/refresh",
    response_model=TokenResponse,
    summary="Refrescar token",
    description="Refresca el token de acceso"
)
async def refresh_token(
    request: RefreshTokenRequest,
    handler=Depends(get_refresh_token_handler)
):
    """Refrescar token"""
    try:
        command = RefreshTokenCommand(refresh_token=request.refresh_token)
        
        result = await handler.handle(command)
        
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            token_type=result["token_type"]
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post(
    "/auth/logout",
    response_model=MessageResponse,
    summary="Cerrar sesión",
    description="Cierra la sesión del usuario"
)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Cerrar sesión"""
    # En una implementación real, aquí se invalidarían los tokens
    return MessageResponse(message="Sesión cerrada exitosamente")


@router.get(
    "/auth/me",
    response_model=UserResponse,
    summary="Obtener perfil",
    description="Obtiene el perfil del usuario autenticado"
)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    handler=Depends(get_current_user_handler)
):
    """Obtener perfil del usuario actual"""
    try:
        query = GetCurrentUserQuery(token=credentials.credentials)
        
        user = await handler.handle(query)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        return UserResponse(
            id=str(user.id),
            email=str(user.email),
            username=str(user.username),
            full_name=str(user.full_name) if user.full_name else None,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get(
    "/auth/verify",
    response_model=VerifyTokenResponse,
    summary="Verificar token",
    description="Verifica si un token es válido"
)
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    handler=Depends(get_verify_token_handler)
):
    """Verificar token"""
    try:
        query = VerifyTokenQuery(token=credentials.credentials)
        
        result = await handler.handle(query)
        
        if result["valid"]:
            payload = result["payload"]
            return VerifyTokenResponse(
                valid=True,
                user={
                    "user_id": payload.get("user_id"),
                    "username": payload.get("sub")
                }
            )
        else:
            return VerifyTokenResponse(
                valid=False,
                error=result.get("error", "Token inválido")
            )
            
    except Exception:
        return VerifyTokenResponse(valid=False, error="Error interno")


@router.get(
    "/auth/users/{user_id}",
    response_model=UserResponse,
    summary="Obtener usuario por ID",
    description="Obtiene un usuario por su ID"
)
async def get_user_by_id(
    user_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    handler=Depends(get_user_by_id_handler),
    current_user_handler=Depends(get_current_user_handler)
):
    """Obtener usuario por ID"""
    try:
        # Verificar que el usuario esté autenticado
        current_query = GetCurrentUserQuery(token=credentials.credentials)
        current_user = await current_user_handler.handle(current_query)
        
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No autorizado"
            )
        
        # Buscar usuario
        query = GetUserByIdQuery(user_id=user_id)
        user = await handler.handle(query)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        return UserResponse(
            id=str(user.id),
            email=str(user.email),
            username=str(user.username),
            full_name=str(user.full_name) if user.full_name else None,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post(
    "/auth/change-password",
    response_model=MessageResponse,
    summary="Cambiar contraseña",
    description="Cambia la contraseña del usuario autenticado"
)
async def change_password(
    request: ChangePasswordRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    handler=Depends(get_change_password_handler),
    current_user_handler=Depends(get_current_user_handler)
):
    """Cambiar contraseña"""
    try:
        # Obtener usuario actual
        current_query = GetCurrentUserQuery(token=credentials.credentials)
        current_user = await current_user_handler.handle(current_query)
        
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No autorizado"
            )
        
        # Verificar que las contraseñas nuevas coincidan
        if request.new_password != request.confirm_new_password:
            raise ValueError("Las contraseñas nuevas no coinciden")
        
        command = ChangePasswordCommand(
            user_id=str(current_user.id),
            current_password=request.current_password,
            new_password=request.new_password,
            confirm_new_password=request.confirm_new_password
        )
        
        await handler.handle(command)
        
        return MessageResponse(message="Contraseña cambiada exitosamente")
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )
