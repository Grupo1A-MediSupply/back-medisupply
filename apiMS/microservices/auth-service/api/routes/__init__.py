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

try:
    from ...application.commands import (
        RegisterUserCommand,
        LoginCommand,
        RefreshTokenCommand,
        ChangePasswordCommand,
        DeactivateUserCommand,
        UpdateProfileCommand,
        VerifyCodeCommand
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
        get_verify_token_handler,
        get_verify_code_handler
    )
except ImportError:
    from application.commands import (
        RegisterUserCommand,
        LoginCommand,
        RefreshTokenCommand,
        ChangePasswordCommand,
        DeactivateUserCommand,
        UpdateProfileCommand,
        VerifyCodeCommand
    )
    from application.queries import (
        GetUserByIdQuery,
        GetCurrentUserQuery,
        VerifyTokenQuery
    )
    from api.dependencies import (
        get_register_user_handler,
        get_login_handler,
        get_refresh_token_handler,
        get_change_password_handler,
        get_deactivate_user_handler,
        get_update_profile_handler,
        get_user_by_id_handler,
        get_current_user_handler,
        get_verify_token_handler,
        get_verify_code_handler
    )

router = APIRouter()
security = HTTPBearer()


# ========== Schemas ==========

class RegisterRequest(BaseModel):
    """Request para registro de usuario"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False


class LoginRequest(BaseModel):
    """Request para login"""
    username: str
    password: str = Field(..., max_length=100)


class RefreshTokenRequest(BaseModel):
    """Request para refresh token"""
    refresh_token: str


class TokenResponse(BaseModel):
    """Response de token"""
    access_token: str
    refresh_token: str
    token_type: str


class LoginResponse(BaseModel):
    """Response de login"""
    message: str
    user_id: str
    email: str
    requires_verification: bool


class UserResponse(BaseModel):
    """Response de usuario"""
    id: str
    email: str
    username: str
    full_name: Optional[str]
    phone_number: Optional[str]
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
        
        return UserResponse(
            id=str(user.id),
            email=str(user.email),
            username=str(user.username),
            full_name=str(user.full_name) if user.full_name else None,
            phone_number=str(user.phone_number) if user.phone_number else None,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
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
    response_model=LoginResponse,
    summary="Iniciar sesión",
    description="Inicia sesión y envía código de verificación por email"
)
async def login(
    request: LoginRequest,
    handler=Depends(get_login_handler)
):
    """Iniciar sesión"""
    try:
        command = LoginCommand(
            username=request.username,
            password=request.password
        )
        
        result = await handler.handle(command)
        
        return LoginResponse(
            message=result["message"],
            user_id=result["user_id"],
            email=result["email"],
            requires_verification=result["requires_verification"]
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        print(f"Error en endpoint login: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
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
            phone_number=str(user.phone_number) if user.phone_number else None,
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
    # (por ejemplo, agregándolos a una blacklist en Redis)
    return MessageResponse(message="Sesión cerrada exitosamente")


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
            phone_number=str(user.phone_number) if user.phone_number else None,
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


# Modelos para verificación de código
class VerifyCodeRequest(BaseModel):
    """Request para verificar código"""
    user_id: str
    code: str


class VerifyCodeResponse(BaseModel):
    """Response para verificación de código"""
    access_token: str
    refresh_token: str
    token_type: str


@router.post(
    "/auth/verify-code",
    response_model=VerifyCodeResponse,
    summary="Verificar código",
    description="Verifica el código de 6 dígitos enviado por email"
)
async def verify_code(
    request: VerifyCodeRequest,
    handler=Depends(get_verify_code_handler)
):
    """Verificar código de autenticación"""
    try:
        command = VerifyCodeCommand(
            user_id=request.user_id,
            code=request.code
        )
        
        result = await handler.handle(command)
        
        return VerifyCodeResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            token_type=result["token_type"]
        )
        
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

