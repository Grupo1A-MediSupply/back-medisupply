"""
Value Objects del dominio de órdenes
"""
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Importar de shared
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from shared.domain.value_objects import EntityId


@dataclass
class OrderItem:
    """Item de una orden"""
    sku_id: str
    qty: int
    price: float
    
    def __post_init__(self):
        if self.qty <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        if self.price < 0:
            raise ValueError("El precio no puede ser negativo")
    
    def subtotal(self) -> float:
        """Calcular subtotal del item"""
        return self.qty * self.price
    
    def to_dict(self) -> dict:
        """Convertir a diccionario"""
        return {
            "sku_id": self.sku_id,
            "qty": self.qty,
            "price": self.price
        }


class OrderStatus(Enum):
    """Estados de una orden"""
    PLACED = "placed"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


__all__ = ['EntityId', 'OrderItem', 'OrderStatus']
