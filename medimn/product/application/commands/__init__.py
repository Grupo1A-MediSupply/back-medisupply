"""
Comandos del servicio de productos
"""
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class BatchData:
    """Datos de un lote"""
    batch: str
    quantity: int
    expiry: Optional[datetime] = None
    location: Optional[str] = None


@dataclass
class CreateProductCommand:
    """Comando para crear un nuevo producto"""
    name: str
    description: Optional[str] = None
    price: float = 0.0
    stock: int = 0
    expiry: Optional[datetime] = None
    lot: Optional[str] = None
    warehouse: Optional[str] = None
    supplier: Optional[str] = None
    category: Optional[str] = None
    batches: Optional[List[BatchData]] = None
    vendor_id: Optional[str] = None
    is_active: bool = True


@dataclass
class UpdateProductCommand:
    """Comando para actualizar un producto"""
    product_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    expiry: Optional[datetime] = None
    lot: Optional[str] = None
    warehouse: Optional[str] = None
    supplier: Optional[str] = None
    category: Optional[str] = None
    batches: Optional[List[BatchData]] = None


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

