"""
Value Objects del dominio de inventario
"""
from .sku import SKU
from .product_name import ProductName
from .stock import Stock
from .location import Location
from .supplier import Supplier

__all__ = ["SKU", "ProductName", "Stock", "Location", "Supplier"]

