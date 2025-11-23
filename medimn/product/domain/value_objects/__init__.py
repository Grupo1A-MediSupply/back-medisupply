"""
Value Objects del dominio de productos
"""
from dataclasses import dataclass
import sys
from pathlib import Path

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from shared.domain.value_objects import Money


@dataclass(frozen=True)
class ProductName:
    """Value Object para nombre de producto"""
    value: str
    
    def __post_init__(self):
        if not self.value or len(self.value) == 0:
            raise ValueError("El nombre del producto no puede estar vacío")
        if len(self.value) > 255:
            raise ValueError("El nombre del producto no puede tener más de 255 caracteres")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ProductDescription:
    """Value Object para descripción de producto"""
    value: str
    
    def __post_init__(self):
        if self.value and len(self.value) > 1000:
            raise ValueError("La descripción no puede tener más de 1000 caracteres")
    
    def __str__(self) -> str:
        return self.value or ""


@dataclass(frozen=True)
class Stock:
    """Value Object para stock de producto"""
    quantity: int
    
    def __post_init__(self):
        if self.quantity < 0:
            raise ValueError("El stock no puede ser negativo")
    
    def __str__(self) -> str:
        return str(self.quantity)
    
    def __int__(self) -> int:
        return self.quantity
    
    def add(self, amount: int) -> 'Stock':
        """Agregar stock"""
        if amount < 0:
            raise ValueError("No se puede agregar una cantidad negativa")
        return Stock(self.quantity + amount)
    
    def remove(self, amount: int) -> 'Stock':
        """Remover stock"""
        if amount < 0:
            raise ValueError("No se puede remover una cantidad negativa")
        if self.quantity - amount < 0:
            raise ValueError("Stock insuficiente")
        return Stock(self.quantity - amount)
    
    def is_available(self, amount: int) -> bool:
        """Verificar si hay stock disponible"""
        return self.quantity >= amount


@dataclass(frozen=True)
class Lot:
    """Value Object para lote de producto"""
    value: str
    
    def __post_init__(self):
        if self.value and len(self.value) > 100:
            raise ValueError("El lote no puede tener más de 100 caracteres")
    
    def __str__(self) -> str:
        return self.value or ""


@dataclass(frozen=True)
class Warehouse:
    """Value Object para bodega"""
    value: str
    
    def __post_init__(self):
        if self.value and len(self.value) > 255:
            raise ValueError("La bodega no puede tener más de 255 caracteres")
    
    def __str__(self) -> str:
        return self.value or ""


@dataclass(frozen=True)
class Supplier:
    """Value Object para proveedor"""
    value: str
    
    def __post_init__(self):
        if self.value and len(self.value) > 255:
            raise ValueError("El proveedor no puede tener más de 255 caracteres")
    
    def __str__(self) -> str:
        return self.value or ""


@dataclass(frozen=True)
class Category:
    """Value Object para categoría"""
    value: str
    
    def __post_init__(self):
        if self.value and len(self.value) > 100:
            raise ValueError("La categoría no puede tener más de 100 caracteres")
    
    def __str__(self) -> str:
        return self.value or ""


@dataclass(frozen=True)
class VendorId:
    """Value Object para ID de vendedor"""
    value: str
    
    def __post_init__(self):
        if self.value and len(self.value) > 100:
            raise ValueError("El vendor ID no puede tener más de 100 caracteres")
    
    def __str__(self) -> str:
        return self.value or ""

