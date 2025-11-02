"""
Entidades del dominio de órdenes
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import uuid4, UUID
import sys
from pathlib import Path

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from shared.domain.entity import Entity
from shared.domain.value_objects import EntityId, Money


class OrderStatus(Enum):
    """Estados de un pedido"""
    PLACED = "PLACED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    PICKED = "PICKED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"


class OrderItem:
    """Value Object para artículo del pedido"""
    
    def __init__(self, sku_id: str, qty: int, price: float):
        if not sku_id or not sku_id.strip():
            raise ValueError("SKU ID es requerido")
        if qty <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        if price < 0:
            raise ValueError("El precio no puede ser negativo")
        
        self.sku_id = sku_id
        self.qty = qty
        self.price = price
        self.subtotal = qty * price
    
    def to_dict(self) -> dict:
        """Convertir a diccionario"""
        return {
            "skuId": self.sku_id,
            "qty": self.qty,
            "price": self.price
        }


class ETA:
    """Value Object para tiempo estimado de llegada"""
    
    def __init__(self, date: datetime, window_minutes: int):
        if window_minutes < 0:
            raise ValueError("La ventana de tiempo no puede ser negativa")
        
        self.date = date
        self.window_minutes = window_minutes
    
    def to_dict(self) -> dict:
        """Convertir a diccionario"""
        return {
            "date": self.date.isoformat(),
            "windowMinutes": self.window_minutes
        }


class Order(Entity):
    """Entidad Order del dominio de órdenes"""
    
    def __init__(
        self,
        order_id: EntityId,
        items: List[OrderItem],
        reservations: Optional[List[str]] = None,
        eta: Optional[ETA] = None,
        status: OrderStatus = OrderStatus.PLACED
    ):
        super().__init__(order_id)
        
        if not items:
            raise ValueError("El pedido debe tener al menos un artículo")
        
        self._items = items
        self._reservations = reservations or []
        self._eta = eta
        self._status = status
        self._totals = self._calculate_totals()
    
    @property
    def items(self) -> List[OrderItem]:
        return self._items
    
    @property
    def reservations(self) -> List[str]:
        return self._reservations
    
    @property
    def eta(self) -> Optional[ETA]:
        return self._eta
    
    @property
    def status(self) -> OrderStatus:
        return self._status
    
    @property
    def totals(self) -> dict:
        """Totales del pedido"""
        return self._totals
    
    def _calculate_totals(self) -> dict:
        """Calcular totales del pedido"""
        subtotal = sum(item.subtotal for item in self._items)
        # Aquí se podrían aplicar reglas de negocio para calcular impuestos y envío
        tax = subtotal * 0.16  # IVA del 16%
        shipping = 0.0
        grand_total = subtotal + tax + shipping
        
        return {
            "subtotal": subtotal,
            "tax": tax,
            "shipping": shipping,
            "grandTotal": grand_total
        }
    
    def add_item(self, item: OrderItem):
        """Agregar artículo al pedido"""
        if self._status != OrderStatus.PLACED:
            raise ValueError("Solo se pueden agregar artículos a pedidos en estado PLACED")
        
        # Verificar si ya existe el SKU
        existing_item = next((i for i in self._items if i.sku_id == item.sku_id), None)
        if existing_item:
            # Actualizar cantidad del artículo existente
            updated_item = OrderItem(
                sku_id=existing_item.sku_id,
                qty=existing_item.qty + item.qty,
                price=existing_item.price
            )
            self._items[self._items.index(existing_item)] = updated_item
        else:
            self._items.append(item)
        
        self._totals = self._calculate_totals()
        self._updated_at = datetime.utcnow()
    
    def remove_item(self, sku_id: str):
        """Eliminar artículo del pedido"""
        if self._status != OrderStatus.PLACED:
            raise ValueError("Solo se pueden eliminar artículos de pedidos en estado PLACED")
        
        item = next((i for i in self._items if i.sku_id == sku_id), None)
        if not item:
            raise ValueError(f"Artículo con SKU {sku_id} no encontrado en el pedido")
        
        self._items.remove(item)
        if not self._items:
            raise ValueError("El pedido debe tener al menos un artículo")
        
        self._totals = self._calculate_totals()
        self._updated_at = datetime.utcnow()
    
    def confirm(self):
        """Confirmar pedido"""
        if self._status != OrderStatus.PLACED:
            raise ValueError("Solo se pueden confirmar pedidos en estado PLACED")
        
        self._status = OrderStatus.CONFIRMED
        self._updated_at = datetime.utcnow()
    
    def cancel(self):
        """Cancelar pedido"""
        if self._status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
            raise ValueError("No se pueden cancelar pedidos enviados o entregados")
        
        self._status = OrderStatus.CANCELLED
        self._updated_at = datetime.utcnow()
    
    def mark_as_picked(self):
        """Marcar como recogido"""
        if self._status != OrderStatus.CONFIRMED:
            raise ValueError("Solo se pueden recoger pedidos confirmados")
        
        self._status = OrderStatus.PICKED
        self._updated_at = datetime.utcnow()
    
    def mark_as_shipped(self):
        """Marcar como enviado"""
        if self._status != OrderStatus.PICKED:
            raise ValueError("Solo se pueden enviar pedidos recogidos")
        
        self._status = OrderStatus.SHIPPED
        self._updated_at = datetime.utcnow()
    
    def mark_as_delivered(self):
        """Marcar como entregado"""
        if self._status != OrderStatus.SHIPPED:
            raise ValueError("Solo se pueden entregar pedidos enviados")
        
        self._status = OrderStatus.DELIVERED
        self._updated_at = datetime.utcnow()
    
    def add_reservation(self, reservation_id: str):
        """Agregar reserva al pedido"""
        if reservation_id not in self._reservations:
            self._reservations.append(reservation_id)
            self._updated_at = datetime.utcnow()
    
    def remove_reservation(self, reservation_id: str):
        """Eliminar reserva del pedido"""
        if reservation_id in self._reservations:
            self._reservations.remove(reservation_id)
            self._updated_at = datetime.utcnow()
    
    def set_eta(self, eta: ETA):
        """Establecer tiempo estimado de llegada"""
        self._eta = eta
        self._updated_at = datetime.utcnow()
    
    @staticmethod
    def create(
        items: List[OrderItem],
        reservations: Optional[List[str]] = None,
        eta: Optional[ETA] = None,
        status: OrderStatus = OrderStatus.PLACED
    ) -> 'Order':
        """Factory method para crear un nuevo pedido"""
        order = Order(
            order_id=EntityId(str(uuid4())),
            items=items,
            reservations=reservations,
            eta=eta,
            status=status
        )
        
        return order

