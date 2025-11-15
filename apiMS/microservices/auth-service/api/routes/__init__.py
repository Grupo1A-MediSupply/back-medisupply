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
    get_verify_token_handler,
    get_token_service,
    get_verification_code_repository
)

router = APIRouter()
security = HTTPBearer()


# ========== Schemas ==========

class RegisterRequest(BaseModel):
    """Request para registro de usuario"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=72, description="Contraseña (máximo 72 caracteres)")
    confirm_password: Optional[str] = None
    full_name: Optional[str] = None
    name: Optional[str] = None  # Alias para full_name según especificación
    phone_number: Optional[str] = None
    phone: Optional[str] = None  # Alias para phone_number según especificación
    role: Optional[str] = Field(None, description="'vendor' o 'client'")
    address: Optional[str] = None
    institution_name: Optional[str] = None
    institutionName: Optional[str] = None  # Alias según especificación
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
    _id: Optional[str] = None  # Alias para compatibilidad
    email: str
    username: Optional[str] = None
    full_name: Optional[str] = None
    name: Optional[str] = None  # Alias según especificación
    phone_number: Optional[str] = None
    phone: Optional[str] = None  # Alias según especificación
    role: Optional[str] = None
    address: Optional[str] = None
    institution_name: Optional[str] = None
    institutionName: Optional[str] = None  # Alias según especificación
    is_active: bool = True
    is_superuser: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    createdAt: Optional[str] = None  # Alias según especificación
    updatedAt: Optional[str] = None  # Alias según especificación


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
        
        # Usar name si está disponible, sino full_name
        name_value = request.name or request.full_name
        phone_value = request.phone or request.phone_number
        institution_value = request.institutionName or request.institution_name
        
        command = RegisterUserCommand(
            email=request.email,
            username=request.username,
            password=request.password,
            confirm_password=request.confirm_password,
            full_name=name_value,
            phone_number=phone_value,
            role=request.role,
            address=request.address,
            institution_name=institution_value,
            is_active=request.is_active,
            is_superuser=request.is_superuser
        )
        
        user = await handler.handle(command)
        
        # Devolver UserResponse según el modelo esperado (compatible con especificación)
        return UserResponse(
            id=str(user.id),
            _id=str(user.id),
            email=str(user.email),
            username=str(user.username),
            full_name=str(user.full_name) if user.full_name else None,
            name=str(user.full_name) if user.full_name else None,
            phone_number=str(user.phone_number) if user.phone_number else None,
            phone=str(user.phone_number) if user.phone_number else None,
            role=str(user.role) if user.role else None,
            address=str(user.address) if user.address else None,
            institution_name=str(user.institution_name) if user.institution_name else None,
            institutionName=str(user.institution_name) if user.institution_name else None,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at,
            createdAt=user.created_at.isoformat() if user.created_at else None,
            updatedAt=user.updated_at.isoformat() if user.updated_at else None
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
        
        # Devolver respuesta según especificación (con mfaRequired)
        user = result.get("user")
        if user:
            return {
                "message": "Login exitoso",
                "token": result.get("access_token", ""),
                "user": {
                    "id": str(user.id),
                    "email": str(user.email),
                    "role": str(user.role) if user.role else None,
                    "name": str(user.full_name) if user.full_name else None
                },
                "mfaRequired": False
            }
        else:
            # Si requiere verificación MFA
            return {
                "message": "Código MFA enviado",
                "mfaRequired": True,
                "userId": result.get("user_id", ""),
                "mfaCode": result.get("mfa_code")  # Solo en desarrollo
            }
        
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
    "/auth/mfa/verify",
    response_model=dict,
    summary="Verificar código MFA",
    description="Verifica el código MFA y devuelve tokens"
)
async def verify_mfa_code(
    request: VerifyCodeRequest
):
    """Verificar código MFA"""
    try:
        from ...application.commands import VerifyCodeCommand
        from ..dependencies import get_verify_code_handler
        
        handler = get_verify_code_handler()
        command = VerifyCodeCommand(
            user_id=request.user_id,
            code=request.code
        )
        
        result = await handler.handle(command)
        
        # Obtener usuario para incluir en respuesta
        from ..dependencies import get_user_by_id_handler
        from ...application.queries import GetUserByIdQuery
        
        user_handler = get_user_by_id_handler()
        user_query = GetUserByIdQuery(user_id=request.user_id)
        user = await user_handler.handle(user_query)
        
        return {
            "message": "MFA verificado exitosamente",
            "token": result.get("access_token", ""),
            "user": {
                "id": str(user.id),
                "email": str(user.email),
                "role": str(user.role) if user.role else None,
                "name": str(user.full_name) if user.full_name else None
            }
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


# Mantener endpoint anterior para compatibilidad (deprecated)
@router.post(
    "/auth/verify-code",
    response_model=dict,
    summary="[DEPRECATED] Verificar código",
    description="DEPRECATED: Usar /auth/mfa/verify en su lugar"
)
async def verify_code(
    request: VerifyCodeRequest
):
    """Verificar código de verificación (deprecated)"""
    return await verify_mfa_code(request)


@router.get(
    "/auth/verification-code/{user_id}",
    response_model=dict,
    summary="Obtener código de verificación",
    description="Obtiene el código de verificación más reciente para un usuario. Útil para desarrollo y testing.",
    tags=["authentication"]
)
async def get_verification_code(
    user_id: str,
    verification_code_repository=Depends(get_verification_code_repository)
):
    """Obtener código de verificación por user_id"""
    try:
        from datetime import datetime
        
        # Obtener el código más reciente
        verification_code = await verification_code_repository.get_latest_code(user_id)
        
        if not verification_code:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontró código de verificación para este usuario"
            )
        
        # Verificar si el código está expirado
        now = datetime.utcnow()
        is_expired = verification_code.expires_at < now
        is_used = verification_code.is_used
        
        return {
            "code": verification_code.code,
            "user_id": verification_code.user_id,
            "email": verification_code.email,
            "expires_at": verification_code.expires_at.isoformat(),
            "is_expired": is_expired,
            "is_used": is_used,
            "is_valid": not is_expired and not is_used,
            "created_at": verification_code.created_at.isoformat(),
            "minutes_remaining": max(0, int((verification_code.expires_at - now).total_seconds() / 60)) if not is_expired else 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener código de verificación: {str(e)}"
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
    "/auth/token",
    response_model=TokenResponse,
    summary="Obtener token",
    description="Obtiene un nuevo token de acceso para el usuario autenticado. Requiere autenticación previa.",
    tags=["authentication"]
)
async def get_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    token_service=Depends(get_token_service),
    handler=Depends(get_current_user_handler)
):
    """Obtener nuevo token de acceso para el usuario autenticado"""
    try:
        # Obtener usuario actual desde el token
        from ...application.queries import GetCurrentUserQuery
        
        query = GetCurrentUserQuery(token=credentials.credentials)
        user = await handler.handle(query)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Generar nuevos tokens
        access_token = token_service.create_access_token(
            user_id=str(user.id),
            username=str(user.username),
            scopes=["read", "write"]
        )
        
        refresh_token = token_service.create_refresh_token(
            user_id=str(user.id),
            username=str(user.username)
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
        
    except HTTPException:
        raise
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
        
        # Devolver UserResponse con todos los campos según especificación
        return UserResponse(
            id=str(user.id),
            _id=str(user.id),
            email=str(user.email),
            username=str(user.username),
            full_name=str(user.full_name) if user.full_name else None,
            name=str(user.full_name) if user.full_name else None,
            phone_number=str(user.phone_number) if user.phone_number else None,
            phone=str(user.phone_number) if user.phone_number else None,
            role=str(user.role) if user.role else None,
            address=str(user.address) if user.address else None,
            institution_name=str(user.institution_name) if user.institution_name else None,
            institutionName=str(user.institution_name) if user.institution_name else None,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at,
            createdAt=user.created_at.isoformat() if user.created_at else None,
            updatedAt=user.updated_at.isoformat() if user.updated_at else None
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
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    handler=Depends(get_verify_token_handler)
):
    """Verificar token
    
    Si no se proporciona token, devuelve valid=False en lugar de error 403.
    Esto permite verificar la validez sin requerir autenticación previa.
    """
    try:
        # Si no hay token, devolver inválido
        if not credentials:
            return VerifyTokenResponse(
                valid=False,
                error="Token no proporcionado"
            )
        
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
        
        # Devolver UserResponse con todos los campos según especificación
        return UserResponse(
            id=str(user.id),
            _id=str(user.id),
            email=str(user.email),
            username=str(user.username),
            full_name=str(user.full_name) if user.full_name else None,
            name=str(user.full_name) if user.full_name else None,
            phone_number=str(user.phone_number) if user.phone_number else None,
            phone=str(user.phone_number) if user.phone_number else None,
            role=str(user.role) if user.role else None,
            address=str(user.address) if user.address else None,
            institution_name=str(user.institution_name) if user.institution_name else None,
            institutionName=str(user.institution_name) if user.institution_name else None,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at,
            createdAt=user.created_at.isoformat() if user.created_at else None,
            updatedAt=user.updated_at.isoformat() if user.updated_at else None
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
