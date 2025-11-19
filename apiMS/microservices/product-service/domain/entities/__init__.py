"""
Entidades del dominio de productos
"""
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass
import sys
from pathlib import Path

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from shared.domain.entity import Entity
from shared.domain.value_objects import EntityId, Money
from ..value_objects import (
    ProductName, ProductDescription, Stock, Lot, Warehouse, 
    Supplier, Category, VendorId
)
from ..events import (
    ProductCreatedEvent,
    ProductUpdatedEvent,
    ProductDeactivatedEvent,
    StockUpdatedEvent,
    LowStockEvent
)


@dataclass
class Batch:
    """Value Object para lote con información adicional"""
    batch: str
    quantity: int
    expiry: Optional[datetime] = None
    location: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convertir a diccionario"""
        return {
            "batch": self.batch,
            "quantity": self.quantity,
            "expiry": self.expiry.isoformat() if self.expiry else None,
            "location": self.location
        }


class Product(Entity):
    """Entidad Product del dominio de productos"""
    
    LOW_STOCK_THRESHOLD = 10
    
    def __init__(
        self,
        product_id: EntityId,
        name: ProductName,
        price: Money,
        description: Optional[ProductDescription] = None,
        stock: Stock = Stock(0),
        expiry: Optional[datetime] = None,
        lot: Optional[Lot] = None,
        warehouse: Optional[Warehouse] = None,
        supplier: Optional[Supplier] = None,
        category: Optional[Category] = None,
        batches: Optional[List[Batch]] = None,
        vendor_id: Optional[VendorId] = None,
        is_active: bool = True
    ):
        super().__init__(product_id)
        self._name = name
        self._price = price
        self._description = description
        self._stock = stock
        self._expiry = expiry
        self._lot = lot
        self._warehouse = warehouse
        self._supplier = supplier
        self._category = category
        self._batches = batches or []
        self._vendor_id = vendor_id
        self._is_active = is_active
    
    @property
    def name(self) -> ProductName:
        return self._name
    
    @property
    def price(self) -> Money:
        return self._price
    
    @property
    def description(self) -> Optional[ProductDescription]:
        return self._description
    
    @property
    def stock(self) -> Stock:
        return self._stock
    
    @property
    def is_active(self) -> bool:
        return self._is_active
    
    @property
    def expiry(self) -> Optional[datetime]:
        return self._expiry
    
    @property
    def lot(self) -> Optional[Lot]:
        return self._lot
    
    @property
    def warehouse(self) -> Optional[Warehouse]:
        return self._warehouse
    
    @property
    def supplier(self) -> Optional[Supplier]:
        return self._supplier
    
    @property
    def category(self) -> Optional[Category]:
        return self._category
    
    @property
    def batches(self) -> List[Batch]:
        return self._batches
    
    @property
    def vendor_id(self) -> Optional[VendorId]:
        return self._vendor_id
    
    def update_name(self, name: ProductName):
        """Actualizar nombre del producto"""
        self._name = name
        self._updated_at = datetime.utcnow()
        self._record_event(ProductUpdatedEvent(str(self._id)))
    
    def update_price(self, price: Money):
        """Actualizar precio del producto"""
        if price.currency != self._price.currency:
            raise ValueError("No se puede cambiar la moneda del producto")
        self._price = price
        self._updated_at = datetime.utcnow()
        self._record_event(ProductUpdatedEvent(str(self._id)))
    
    def update_description(self, description: ProductDescription):
        """Actualizar descripción del producto"""
        self._description = description
        self._updated_at = datetime.utcnow()
        self._record_event(ProductUpdatedEvent(str(self._id)))
    
    def add_stock(self, amount: int):
        """Agregar stock"""
        old_stock = self._stock.quantity
        self._stock = self._stock.add(amount)
        self._updated_at = datetime.utcnow()
        
        self._record_event(StockUpdatedEvent(
            product_id=str(self._id),
            old_stock=old_stock,
            new_stock=self._stock.quantity
        ))
    
    def remove_stock(self, amount: int):
        """Remover stock"""
        if not self._stock.is_available(amount):
            raise ValueError(f"Stock insuficiente. Disponible: {self._stock.quantity}, Requerido: {amount}")
        
        old_stock = self._stock.quantity
        self._stock = self._stock.remove(amount)
        self._updated_at = datetime.utcnow()
        
        self._record_event(StockUpdatedEvent(
            product_id=str(self._id),
            old_stock=old_stock,
            new_stock=self._stock.quantity
        ))
        
        # Verificar si el stock es bajo
        if self._stock.quantity <= self.LOW_STOCK_THRESHOLD:
            self._record_event(LowStockEvent(
                product_id=str(self._id),
                current_stock=self._stock.quantity,
                threshold=self.LOW_STOCK_THRESHOLD
            ))
    
    def deactivate(self):
        """Desactivar producto"""
        if not self._is_active:
            raise ValueError("El producto ya está desactivado")
        
        self._is_active = False
        self._updated_at = datetime.utcnow()
        self._record_event(ProductDeactivatedEvent(str(self._id)))
    
    def activate(self):
        """Activar producto"""
        if self._is_active:
            raise ValueError("El producto ya está activo")
        
        self._is_active = True
        self._updated_at = datetime.utcnow()
    
    @staticmethod
    def create(
        product_id: EntityId,
        name: ProductName,
        price: Money,
        description: Optional[ProductDescription] = None,
        stock: Stock = Stock(0),
        expiry: Optional[datetime] = None,
        lot: Optional[Lot] = None,
        warehouse: Optional[Warehouse] = None,
        supplier: Optional[Supplier] = None,
        category: Optional[Category] = None,
        batches: Optional[List[Batch]] = None,
        vendor_id: Optional[VendorId] = None,
        is_active: bool = True
    ) -> 'Product':
        """Factory method para crear un nuevo producto"""
        product = Product(
            product_id=product_id,
            name=name,
            price=price,
            description=description,
            stock=stock,
            expiry=expiry,
            lot=lot,
            warehouse=warehouse,
            supplier=supplier,
            category=category,
            batches=batches,
            vendor_id=vendor_id,
            is_active=is_active
        )
        
        # Registrar evento de dominio
        product._record_event(ProductCreatedEvent(
            product_id=str(product_id),
            name=str(name),
            price=price.amount
        ))
        
        return product

