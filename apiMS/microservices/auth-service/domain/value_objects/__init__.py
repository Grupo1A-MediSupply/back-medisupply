"""
Value Objects del dominio de autenticación
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Username:
    """Value Object para nombre de usuario"""
    value: str
    
    def __post_init__(self):
        if not self.value or len(self.value) < 3:
            raise ValueError("El username debe tener al menos 3 caracteres")
        if len(self.value) > 50:
            raise ValueError("El username no puede tener más de 50 caracteres")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class HashedPassword:
    """Value Object para contraseña hasheada"""
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("La contraseña hasheada no puede estar vacía")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class FullName:
    """Value Object para nombre completo"""
    value: str
    
    def __post_init__(self):
        if self.value and len(self.value) > 100:
            raise ValueError("El nombre completo no puede tener más de 100 caracteres")
    
    def __str__(self) -> str:
        return self.value or ""

