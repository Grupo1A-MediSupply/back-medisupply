"""
Comandos del servicio de productos
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class CreateProductCommand:
    """Comando para crear un nuevo producto"""
    name: str
    description: Optional[str]
    price: float
    stock: int = 0
    is_active: bool = True


@dataclass
class UpdateProductCommand:
    """Comando para actualizar un producto"""
    product_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None


@dataclass
class AddStockCommand:
    """Comando para agregar stock"""
    product_id: str
    amount: int


@dataclass
class RemoveStockCommand:
    """Comando para remover stock"""
    product_id: str
    amount: int


@dataclass
class DeactivateProductCommand:
    """Comando para desactivar producto"""
    product_id: str


@dataclass
class ActivateProductCommand:
    """Comando para activar producto"""
    product_id: str


@dataclass
class DeleteProductCommand:
    """Comando para eliminar producto"""
    product_id: str

