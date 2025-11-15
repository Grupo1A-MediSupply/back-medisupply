"""
Entidad InventoryItem del dominio de inventario
"""
from datetime import datetime
from typing import Optional
import sys
from pathlib import Path

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from shared.domain.entity import Entity
from shared.domain.value_objects import EntityId
from ..value_objects import SKU, ProductName, Stock, Location, Supplier


class InventoryItem(Entity):
    """Entidad que representa un item de inventario"""
    
    def __init__(
        self,
        item_id: EntityId,
        sku: SKU,
        name: ProductName,
        stock: Stock,
        min_stock: Stock,
        max_stock: Stock,
        location: Location,
        supplier: Optional[Supplier] = None,
        category: Optional[str] = None,
        unit_price: Optional[float] = None,
        is_active: bool = True
    ):
        super().__init__(item_id)
        self._sku = sku
        self._name = name
        self._stock = stock
        self._min_stock = min_stock
        self._max_stock = max_stock
        self._location = location
        self._supplier = supplier
        self._category = category
        self._unit_price = unit_price
        self._is_active = is_active
    
    @property
    def sku(self) -> SKU:
        return self._sku
    
    @property
    def name(self) -> ProductName:
        return self._name
    
    @property
    def stock(self) -> Stock:
        return self._stock
    
    @property
    def min_stock(self) -> Stock:
        return self._min_stock
    
    @property
    def max_stock(self) -> Stock:
        return self._max_stock
    
    @property
    def location(self) -> Location:
        return self._location
    
    @property
    def supplier(self) -> Optional[Supplier]:
        return self._supplier
    
    @property
    def category(self) -> Optional[str]:
        return self._category
    
    @property
    def unit_price(self) -> Optional[float]:
        return self._unit_price
    
    @property
    def is_active(self) -> bool:
        return self._is_active
    
    def add_stock(self, quantity: int):
        """Agregar stock al item"""
        if quantity <= 0:
            raise ValueError("La cantidad debe ser positiva")
        if not self._is_active:
            raise ValueError("No se puede modificar stock de item inactivo")
        
        new_stock = self._stock.value + quantity
        if new_stock > self._max_stock.value:
            raise ValueError(f"Stock máximo excedido (max: {self._max_stock.value})")
        
        self._stock = Stock(new_stock)
        self._updated_at = datetime.utcnow()
    
    def remove_stock(self, quantity: int):
        """Quitar stock del item"""
        if quantity <= 0:
            raise ValueError("La cantidad debe ser positiva")
        if not self._is_active:
            raise ValueError("No se puede modificar stock de item inactivo")
        
        new_stock = self._stock.value - quantity
        if new_stock < 0:
            raise ValueError("Stock insuficiente")
        
        self._stock = Stock(new_stock)
        self._updated_at = datetime.utcnow()
    
    def update_location(self, new_location: Location):
        """Actualizar ubicación del item"""
        if not self._is_active:
            raise ValueError("No se puede modificar item inactivo")
        
        self._location = new_location
        self._updated_at = datetime.utcnow()
    
    def deactivate(self):
        """Desactivar item"""
        if not self._is_active:
            raise ValueError("El item ya está desactivado")
        
        self._is_active = False
        self._updated_at = datetime.utcnow()
    
    def activate(self):
        """Activar item"""
        if self._is_active:
            raise ValueError("El item ya está activo")
        
        self._is_active = True
        self._updated_at = datetime.utcnow()
    
    def is_low_stock(self) -> bool:
        """Verificar si el stock está bajo"""
        return self._stock.value <= self._min_stock.value
    
    def is_out_of_stock(self) -> bool:
        """Verificar si está sin stock"""
        return self._stock.value == 0
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at

