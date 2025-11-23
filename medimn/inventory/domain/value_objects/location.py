"""
Value Object para Location
"""
from typing import Any, Optional


class Location:
    """Ubicación del item en el almacén"""
    
    def __init__(self, value: str, warehouse: Optional[str] = None, section: Optional[str] = None):
        if not value:
            raise ValueError("La ubicación no puede estar vacía")
        if len(value) > 100:
            raise ValueError("La ubicación no puede tener más de 100 caracteres")
        
        self._value = value.strip()
        self._warehouse = warehouse.strip() if warehouse else None
        self._section = section.strip() if section else None
    
    @property
    def value(self) -> str:
        return self._value
    
    @property
    def warehouse(self) -> Optional[str]:
        return self._warehouse
    
    @property
    def section(self) -> Optional[str]:
        return self._section
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Location):
            return False
        return self._value == other._value
    
    def __hash__(self) -> int:
        return hash(self._value)
    
    def __str__(self) -> str:
        return self._value
    
    def __repr__(self) -> str:
        return f"Location('{self._value}')"

