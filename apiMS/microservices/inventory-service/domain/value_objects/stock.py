"""
Value Object para Stock
"""
from typing import Any


class Stock:
    """Cantidad de stock disponible"""
    
    def __init__(self, value: int):
        if value < 0:
            raise ValueError("El stock no puede ser negativo")
        
        self._value = value
    
    @property
    def value(self) -> int:
        return self._value
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Stock):
            return False
        return self._value == other._value
    
    def __hash__(self) -> int:
        return hash(self._value)
    
    def __str__(self) -> str:
        return str(self._value)
    
    def __repr__(self) -> str:
        return f"Stock({self._value})"
    
    def __lt__(self, other: 'Stock') -> bool:
        return self._value < other._value
    
    def __gt__(self, other: 'Stock') -> bool:
        return self._value > other._value

