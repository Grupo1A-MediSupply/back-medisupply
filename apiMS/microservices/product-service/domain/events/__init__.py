"""
Eventos de dominio del servicio de productos
"""
from typing import Dict, Any
import sys
from pathlib import Path

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from shared.domain.events import DomainEvent


class ProductCreatedEvent(DomainEvent):
    """Evento que se dispara cuando se crea un producto"""
    
    def __init__(self, product_id: str, name: str, price: float):
        super().__init__()
        self.product_id = product_id
        self.name = name
        self.price = price
        self.aggregate_id = product_id
    
    def _event_data(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "price": self.price
        }


class ProductUpdatedEvent(DomainEvent):
    """Evento que se dispara cuando se actualiza un producto"""
    
    def __init__(self, product_id: str):
        super().__init__()
        self.product_id = product_id
        self.aggregate_id = product_id
    
    def _event_data(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id
        }


class ProductDeactivatedEvent(DomainEvent):
    """Evento que se dispara cuando se desactiva un producto"""
    
    def __init__(self, product_id: str):
        super().__init__()
        self.product_id = product_id
        self.aggregate_id = product_id
    
    def _event_data(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id
        }


class StockUpdatedEvent(DomainEvent):
    """Evento que se dispara cuando se actualiza el stock"""
    
    def __init__(self, product_id: str, old_stock: int, new_stock: int):
        super().__init__()
        self.product_id = product_id
        self.old_stock = old_stock
        self.new_stock = new_stock
        self.aggregate_id = product_id
    
    def _event_data(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id,
            "old_stock": self.old_stock,
            "new_stock": self.new_stock
        }


class LowStockEvent(DomainEvent):
    """Evento que se dispara cuando el stock es bajo"""
    
    def __init__(self, product_id: str, current_stock: int, threshold: int):
        super().__init__()
        self.product_id = product_id
        self.current_stock = current_stock
        self.threshold = threshold
        self.aggregate_id = product_id
    
    def _event_data(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id,
            "current_stock": self.current_stock,
            "threshold": self.threshold
        }

