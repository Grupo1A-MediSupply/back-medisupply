"""
Queries del servicio de inventario
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class GetInventoryItemByIdQuery:
    """Query para obtener item por ID"""
    item_id: str


@dataclass
class GetInventoryItemBySKUQuery:
    """Query para obtener item por SKU"""
    sku: str


@dataclass
class GetAllInventoryItemsQuery:
    """Query para obtener todos los items"""
    active_only: bool = True
    low_stock_only: bool = False
    category: Optional[str] = None

