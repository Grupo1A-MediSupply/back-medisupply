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


@dataclass(frozen=True)
class PhoneNumber:
    """Value Object para número de teléfono"""
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("El número de teléfono no puede estar vacío")
        
        # Validar formato básico de teléfono (números, +, -, espacios, paréntesis)
        import re
        phone_pattern = r'^[\+]?[0-9\s\-\(\)]{7,15}$'
        if not re.match(phone_pattern, self.value):
            raise ValueError("El formato del número de teléfono no es válido")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class UserRole:
    """Value Object para rol de usuario"""
    value: str
    
    def __post_init__(self):
        valid_roles = ["vendor", "client"]
        if self.value not in valid_roles:
            raise ValueError(f"El rol debe ser uno de: {', '.join(valid_roles)}")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Address:
    """Value Object para dirección"""
    value: str
    
    def __post_init__(self):
        if self.value and len(self.value) > 255:
            raise ValueError("La dirección no puede tener más de 255 caracteres")
    
    def __str__(self) -> str:
        return self.value or ""


@dataclass(frozen=True)
class InstitutionName:
    """Value Object para nombre de institución"""
    value: str
    
    def __post_init__(self):
        if self.value and len(self.value) > 255:
            raise ValueError("El nombre de institución no puede tener más de 255 caracteres")
    
    def __str__(self) -> str:
        return self.value or ""
