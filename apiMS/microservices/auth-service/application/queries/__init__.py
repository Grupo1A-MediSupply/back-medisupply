"""
Queries del servicio de autenticación
"""
from dataclasses import dataclass


@dataclass
class GetUserByIdQuery:
    """Query para obtener usuario por ID"""
    user_id: str


@dataclass
class GetUserByUsernameQuery:
    """Query para obtener usuario por username"""
    username: str


@dataclass
class GetUserByEmailQuery:
    """Query para obtener usuario por email"""
    email: str


@dataclass
class VerifyTokenQuery:
    """Query para verificar token"""
    token: str


@dataclass
class GetCurrentUserQuery:
    """Query para obtener usuario actual desde token"""
    token: str

