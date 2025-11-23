"""
Value Object para Supplier
"""
from typing import Any, Optional


class Supplier:
    """Proveedor del item"""
    
    def __init__(self, name: str, contact: Optional[str] = None):
        if not name:
            raise ValueError("El nombre del proveedor no puede estar vacío")
        if len(name) > 200:
            raise ValueError("El nombre del proveedor no puede tener más de 200 caracteres")
        
        self._name = name.strip()
        self._contact = contact.strip() if contact else None
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def contact(self) -> Optional[str]:
        return self._contact
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Supplier):
            return False
        return self._name == other._name
    
    def __hash__(self) -> int:
        return hash(self._name)
    
    def __str__(self) -> str:
        return self._name
    
    def __repr__(self) -> str:
        return f"Supplier('{self._name}')"

