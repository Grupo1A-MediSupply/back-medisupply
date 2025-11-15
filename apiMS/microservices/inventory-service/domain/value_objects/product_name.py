"""
Value Object para ProductName
"""
from typing import Any


class ProductName:
    """Nombre del producto en inventario"""
    
    def __init__(self, value: str):
        if not value:
            raise ValueError("El nombre del producto no puede estar vacío")
        if len(value) < 3:
            raise ValueError("El nombre debe tener al menos 3 caracteres")
        if len(value) > 200:
            raise ValueError("El nombre no puede tener más de 200 caracteres")
        
        self._value = value.strip()
    
    @property
    def value(self) -> str:
        return self._value
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ProductName):
            return False
        return self._value == other._value
    
    def __hash__(self) -> int:
        return hash(self._value)
    
    def __str__(self) -> str:
        return self._value
    
    def __repr__(self) -> str:
        return f"ProductName('{self._value}')"

