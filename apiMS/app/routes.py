"""
Rutas de autenticación
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .auth_service import AuthService
from .schemas import (
    LoginRequest, RefreshTokenRequest, UserCreate, UserResponse, 
    Token, TokenVerifyResponse, LogoutResponse
)
from .database import get_db

router = APIRouter()
security = HTTPBearer()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Dependency para obtener servicio de autenticación"""
    return AuthService(db)


@router.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar usuario",
    description="Registra un nuevo usuario en el sistema"
)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Registrar nuevo usuario"""
    try:
        user = auth_service.create_user(user_data)
        return UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post(
    "/auth/login",
    response_model=Token,
    summary="Iniciar sesión",
    description="Inicia sesión y obtiene tokens de acceso"
)
async def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Iniciar sesión"""
    try:
        return auth_service.login(login_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post(
    "/auth/refresh",
    response_model=Token,
    summary="Refrescar token",
    description="Refresca el token de acceso usando el token de refresco"
)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Refrescar token"""
    try:
        return auth_service.refresh_token(refresh_data)
    except HTTPException:
        raise
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
async def get_current_user_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Obtener perfil del usuario actual"""
    try:
        user = auth_service.get_current_user(credentials.credentials)
        return UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post(
    "/auth/logout",
    response_model=LogoutResponse,
    summary="Cerrar sesión",
    description="Cierra la sesión del usuario (invalidar tokens)"
)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Cerrar sesión"""
    # En una implementación real, aquí se invalidarían los tokens
    # (por ejemplo, agregándolos a una blacklist en Redis)
    # Por ahora, solo devolvemos un mensaje de éxito
    return LogoutResponse(message="Sesión cerrada exitosamente")


@router.get(
    "/auth/verify",
    response_model=TokenVerifyResponse,
    summary="Verificar token",
    description="Verifica si un token es válido"
)
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Verificar token"""
    try:
        user = auth_service.get_current_user(credentials.credentials)
        return TokenVerifyResponse(
            valid=True,
            user={
                "id": str(user.id),
                "username": user.username,
                "email": user.email
            }
        )
    except HTTPException:
        return TokenVerifyResponse(valid=False, error="Token inválido")
    except Exception:
        return TokenVerifyResponse(valid=False, error="Error interno")

