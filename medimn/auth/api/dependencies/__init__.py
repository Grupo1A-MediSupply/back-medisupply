"""
Dependencias de FastAPI
"""
from sqlalchemy.orm import Session
from fastapi import Depends
import sys
from pathlib import Path

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from ...infrastructure.database import get_db
from ...infrastructure.repositories import SQLAlchemyUserRepository
from ...infrastructure.adapters import BcryptPasswordHasher, JWTTokenService
from ...infrastructure.verification_code_repository import VerificationCodeRepository
# Email service removido - ya no se envía email
# from ...infrastructure.email_service import email_service
from ...infrastructure.config import get_settings
from ...application.handlers import (
    RegisterUserCommandHandler,
    LoginCommandHandler,
    RefreshTokenCommandHandler,
    ChangePasswordCommandHandler,
    DeactivateUserCommandHandler,
    UpdateProfileCommandHandler,
    GetUserByIdQueryHandler,
    GetUserByUsernameQueryHandler,
    GetCurrentUserQueryHandler,
    VerifyTokenQueryHandler,
    VerifyCodeCommandHandler
)

settings = get_settings()


# Repositorios
def get_user_repository(db: Session = Depends(get_db)) -> SQLAlchemyUserRepository:
    """Obtener repositorio de usuarios"""
    return SQLAlchemyUserRepository(db)


def get_verification_code_repository(db: Session = Depends(get_db)) -> VerificationCodeRepository:
    """Obtener repositorio de códigos de verificación"""
    return VerificationCodeRepository(db)


# Adaptadores
def get_password_hasher() -> BcryptPasswordHasher:
    """Obtener password hasher"""
    return BcryptPasswordHasher()


def get_token_service() -> JWTTokenService:
    """Obtener token service"""
    return JWTTokenService(
        secret_key=settings.secret_key,
        algorithm=settings.algorithm,
        access_token_expire_minutes=settings.access_token_expire_minutes
    )


# Command Handlers
def get_register_user_handler(
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository),
    password_hasher: BcryptPasswordHasher = Depends(get_password_hasher)
) -> RegisterUserCommandHandler:
    """Obtener handler de registro de usuario"""
    return RegisterUserCommandHandler(user_repository, password_hasher)


def get_login_handler(
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository),
    password_hasher: BcryptPasswordHasher = Depends(get_password_hasher),
    verification_code_repository: VerificationCodeRepository = Depends(get_verification_code_repository)
) -> LoginCommandHandler:
    """Obtener handler de login"""
    return LoginCommandHandler(user_repository, password_hasher, verification_code_repository)


def get_refresh_token_handler(
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository),
    token_service: JWTTokenService = Depends(get_token_service)
) -> RefreshTokenCommandHandler:
    """Obtener handler de refresh token"""
    return RefreshTokenCommandHandler(user_repository, token_service)


def get_change_password_handler(
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository),
    password_hasher: BcryptPasswordHasher = Depends(get_password_hasher)
) -> ChangePasswordCommandHandler:
    """Obtener handler de cambio de contraseña"""
    return ChangePasswordCommandHandler(user_repository, password_hasher)


def get_deactivate_user_handler(
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository)
) -> DeactivateUserCommandHandler:
    """Obtener handler de desactivación de usuario"""
    return DeactivateUserCommandHandler(user_repository)


def get_update_profile_handler(
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository)
) -> UpdateProfileCommandHandler:
    """Obtener handler de actualización de perfil"""
    return UpdateProfileCommandHandler(user_repository)


# Query Handlers
def get_user_by_id_handler(
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository)
) -> GetUserByIdQueryHandler:
    """Obtener handler de query por ID"""
    return GetUserByIdQueryHandler(user_repository)


def get_user_by_username_handler(
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository)
) -> GetUserByUsernameQueryHandler:
    """Obtener handler de query por username"""
    return GetUserByUsernameQueryHandler(user_repository)


def get_current_user_handler(
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository),
    token_service: JWTTokenService = Depends(get_token_service)
) -> GetCurrentUserQueryHandler:
    """Obtener handler de usuario actual"""
    return GetCurrentUserQueryHandler(user_repository, token_service)


def get_verify_token_handler(
    token_service: JWTTokenService = Depends(get_token_service)
) -> VerifyTokenQueryHandler:
    """Obtener handler de verificación de token"""
    return VerifyTokenQueryHandler(token_service)


def get_verify_code_handler(
    verification_code_repository: VerificationCodeRepository = Depends(get_verification_code_repository),
    token_service: JWTTokenService = Depends(get_token_service)
) -> VerifyCodeCommandHandler:
    """Obtener handler de verificación de código"""
    return VerifyCodeCommandHandler(verification_code_repository, token_service)

