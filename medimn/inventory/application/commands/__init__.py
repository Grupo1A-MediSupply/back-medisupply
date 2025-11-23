"""
Comandos del servicio de inventario
"""
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class CreateInventoryItemCommand:
    """Comando para crear un item de inventario"""
    sku: str
    name: str
    stock: int = 0
    min_stock: int = 0
    max_stock: int = 1000
    location: str = "Almacén Principal"
    supplier: Optional[str] = None
    category: Optional[str] = None
    unit_price: Optional[float] = None


@dataclass
class UpdateInventoryItemCommand:
    """Comando para actualizar un item de inventario"""
    item_id: str
    name: Optional[str] = None
    min_stock: Optional[int] = None
    max_stock: Optional[int] = None
    location: Optional[str] = None
    category: Optional[str] = None
    unit_price: Optional[float] = None


@dataclass
class AddStockCommand:
    """Comando para agregar stock"""
    item_id: str
    quantity: int


@dataclass
class RemoveStockCommand:
    """Comando para remover stock"""
    item_id: str
    quantity: int


@dataclass
class UpdateLocationCommand:
    """Comando para actualizar ubicación"""
    item_id: str
    location: str


@dataclass
class DeactivateItemCommand:
    """Comando para desactivar item"""
    item_id: str


@dataclass
class ActivateItemCommand:
    """Comando para activar item"""
    item_id: str


@dataclass
class BulkImportCommand:
    """Comando para importación masiva"""
    items: List[dict]  # Lista de diccionarios con datos de items

