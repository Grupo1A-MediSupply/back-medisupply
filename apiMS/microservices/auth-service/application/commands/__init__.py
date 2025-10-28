"""
Comandos del servicio de autenticación
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class RegisterUserCommand:
    """Comando para registrar un nuevo usuario"""
    email: str
    username: str
    password: str
    confirm_password: Optional[str] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False


@dataclass
class LoginCommand:
    """Comando para iniciar sesión"""
    username: str
    password: str


@dataclass
class RefreshTokenCommand:
    """Comando para refrescar token"""
    refresh_token: str


@dataclass
class ChangePasswordCommand:
    """Comando para cambiar contraseña"""
    user_id: str
    current_password: str
    new_password: str
    confirm_new_password: str


@dataclass
class DeactivateUserCommand:
    """Comando para desactivar usuario"""
    user_id: str


@dataclass
class UpdateProfileCommand:
    """Comando para actualizar perfil"""
    user_id: str
    full_name: Optional[str] = None


@dataclass
class VerifyCodeCommand:
    """Comando para verificar código"""
    user_id: str
    code: str


@dataclass
class ResendCodeCommand:
    """Comando para reenviar código"""
    user_id: str
