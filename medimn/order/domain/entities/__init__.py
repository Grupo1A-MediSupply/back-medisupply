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
    RETURNED = "RETURNED"


class ReturnStatus(Enum):
    """Estados de devolución"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"


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
        status: OrderStatus = OrderStatus.PLACED,
        order_number: Optional[str] = None,
        client_id: Optional[str] = None,
        vendor_id: Optional[str] = None,
        delivery_address: Optional[str] = None,
        delivery_date: Optional[datetime] = None,
        contact_name: Optional[str] = None,
        contact_phone: Optional[str] = None,
        notes: Optional[str] = None,
        route_id: Optional[str] = None,
        return_requested: bool = False,
        return_reason: Optional[str] = None,
        return_status: Optional[ReturnStatus] = None
    ):
        super().__init__(order_id)
        
        if not items:
            raise ValueError("El pedido debe tener al menos un artículo")
        
        self._items = items
        self._reservations = reservations or []
        self._eta = eta
        self._status = status
        self._order_number = order_number or self._generate_order_number()
        self._client_id = client_id
        self._vendor_id = vendor_id
        self._delivery_address = delivery_address
        self._delivery_date = delivery_date
        self._contact_name = contact_name
        self._contact_phone = contact_phone
        self._notes = notes
        self._route_id = route_id
        self._return_requested = return_requested
        self._return_reason = return_reason
        self._return_status = return_status
        self._totals = self._calculate_totals()
    
    def _generate_order_number(self) -> str:
        """Generar número de orden único"""
        from datetime import datetime
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        import random
        random_part = random.randint(1000, 9999)
        return f"ORD-{timestamp}-{random_part}"
    
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
    
    @property
    def order_number(self) -> str:
        return self._order_number
    
    @property
    def client_id(self) -> Optional[str]:
        return self._client_id
    
    @property
    def vendor_id(self) -> Optional[str]:
        return self._vendor_id
    
    @property
    def delivery_address(self) -> Optional[str]:
        return self._delivery_address
    
    @property
    def delivery_date(self) -> Optional[datetime]:
        return self._delivery_date
    
    @property
    def contact_name(self) -> Optional[str]:
        return self._contact_name
    
    @property
    def contact_phone(self) -> Optional[str]:
        return self._contact_phone
    
    @property
    def notes(self) -> Optional[str]:
        return self._notes
    
    @property
    def route_id(self) -> Optional[str]:
        return self._route_id
    
    @property
    def return_requested(self) -> bool:
        return self._return_requested
    
    @property
    def return_reason(self) -> Optional[str]:
        return self._return_reason
    
    @property
    def return_status(self) -> Optional[ReturnStatus]:
        return self._return_status
    
    @property
    def total_amount(self) -> float:
        """Total amount del pedido"""
        return self._totals.get("grandTotal", 0.0)
    
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
    
    def update_delivery_info(
        self,
        delivery_address: Optional[str] = None,
        delivery_date: Optional[datetime] = None,
        contact_name: Optional[str] = None,
        contact_phone: Optional[str] = None,
        notes: Optional[str] = None,
        route_id: Optional[str] = None
    ):
        """Actualizar información de entrega"""
        if delivery_address is not None:
            self._delivery_address = delivery_address
        if delivery_date is not None:
            self._delivery_date = delivery_date
        if contact_name is not None:
            self._contact_name = contact_name
        if contact_phone is not None:
            self._contact_phone = contact_phone
        if notes is not None:
            self._notes = notes
        if route_id is not None:
            self._route_id = route_id
        self._updated_at = datetime.utcnow()
    
    def request_return(self, reason: str):
        """Solicitar devolución de la orden"""
        if self._status != OrderStatus.DELIVERED:
            raise ValueError("Solo se pueden devolver órdenes entregadas")
        
        self._return_requested = True
        self._return_reason = reason
        self._return_status = ReturnStatus.PENDING
        self._updated_at = datetime.utcnow()
    
    def approve_return(self):
        """Aprobar devolución"""
        if not self._return_requested:
            raise ValueError("No hay solicitud de devolución pendiente")
        
        self._return_status = ReturnStatus.APPROVED
        self._updated_at = datetime.utcnow()
    
    def reject_return(self):
        """Rechazar devolución"""
        if not self._return_requested:
            raise ValueError("No hay solicitud de devolución pendiente")
        
        self._return_status = ReturnStatus.REJECTED
        self._updated_at = datetime.utcnow()
    
    def complete_return(self):
        """Completar devolución"""
        if not self._return_requested:
            raise ValueError("No hay solicitud de devolución pendiente")
        
        self._return_status = ReturnStatus.COMPLETED
        self._status = OrderStatus.RETURNED
        self._updated_at = datetime.utcnow()
    
    @staticmethod
    def create(
        items: List[OrderItem],
        reservations: Optional[List[str]] = None,
        eta: Optional[ETA] = None,
        status: OrderStatus = OrderStatus.PLACED,
        order_number: Optional[str] = None,
        client_id: Optional[str] = None,
        vendor_id: Optional[str] = None,
        delivery_address: Optional[str] = None,
        delivery_date: Optional[datetime] = None,
        contact_name: Optional[str] = None,
        contact_phone: Optional[str] = None,
        notes: Optional[str] = None,
        route_id: Optional[str] = None
    ) -> 'Order':
        """Factory method para crear un nuevo pedido"""
        order = Order(
            order_id=EntityId(str(uuid4())),
            items=items,
            reservations=reservations,
            eta=eta,
            status=status,
            order_number=order_number,
            client_id=client_id,
            vendor_id=vendor_id,
            delivery_address=delivery_address,
            delivery_date=delivery_date,
            contact_name=contact_name,
            contact_phone=contact_phone,
            notes=notes,
            route_id=route_id
        )
        
        return order

