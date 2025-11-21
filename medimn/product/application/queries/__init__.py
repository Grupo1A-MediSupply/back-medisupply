"""
Queries del servicio de productos
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class GetProductByIdQuery:
    """Query para obtener producto por ID"""
    product_id: str


@dataclass
class GetProductByNameQuery:
    """Query para obtener producto por nombre"""
    name: str


@dataclass
class GetAllProductsQuery:
    """Query para obtener todos los productos"""
    active_only: bool = True
    search: Optional[str] = None
    category: Optional[str] = None
    low_stock_only: bool = False


@dataclass
class GetProductStockQuery:
    """Query para obtener el stock de un producto"""
    product_id: str

