"""
Value Objects compartidos
"""
from dataclasses import dataclass
from typing import Any
import re


@dataclass(frozen=True)
class Email:
    """Value Object para email"""
    value: str
    
    def __post_init__(self):
        if not self._is_valid():
            raise ValueError(f"Email inválido: {self.value}")
    
    def _is_valid(self) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, self.value))
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class EntityId:
    """Value Object para ID de entidad"""
    value: str
    
    def __post_init__(self):
        if not self.value or len(self.value) == 0:
            raise ValueError("El ID no puede estar vacío")
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, EntityId):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class Money:
    """Value Object para dinero"""
    amount: float
    currency: str = "USD"
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("El monto no puede ser negativo")
        if len(self.currency) != 3:
            raise ValueError("La moneda debe tener 3 caracteres")
    
    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"
    
    def __add__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("No se pueden sumar monedas diferentes")
        return Money(self.amount + other.amount, self.currency)
    
    def __sub__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("No se pueden restar monedas diferentes")
        return Money(self.amount - other.amount, self.currency)

