"""
Value Object para SKU (Stock Keeping Unit)
"""
from typing import Any


class SKU:
    """SKU - Identificador único de producto"""
    
    def __init__(self, value: str):
        if not value:
            raise ValueError("SKU no puede estar vacío")
        if len(value) < 3:
            raise ValueError("SKU debe tener al menos 3 caracteres")
        if len(value) > 50:
            raise ValueError("SKU no puede tener más de 50 caracteres")
        
        self._value = value.upper().strip()
    
    @property
    def value(self) -> str:
        return self._value
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, SKU):
            return False
        return self._value == other._value
    
    def __hash__(self) -> int:
        return hash(self._value)
    
    def __str__(self) -> str:
        return self._value
    
    def __repr__(self) -> str:
        return f"SKU('{self._value}')"

