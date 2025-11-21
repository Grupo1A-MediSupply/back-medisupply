"""
Comandos del servicio de órdenes
"""
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class CreateOrderCommand:
    """Comando para crear una orden"""
    items: List[dict]  # [{"skuId": str, "qty": int, "price": float}]
    eta: Optional[dict] = None  # {"date": datetime, "windowMinutes": int}
    reservations: Optional[List[str]] = None
    client_id: Optional[str] = None
    vendor_id: Optional[str] = None
    delivery_address: Optional[str] = None
    delivery_date: Optional[datetime] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    notes: Optional[str] = None
    route_id: Optional[str] = None


@dataclass
class UpdateOrderCommand:
    """Comando para actualizar una orden"""
    order_id: str
    items: Optional[List[dict]] = None
    eta: Optional[dict] = None
    status: Optional[str] = None
    delivery_address: Optional[str] = None
    delivery_date: Optional[datetime] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    notes: Optional[str] = None
    route_id: Optional[str] = None


@dataclass
class ConfirmOrderCommand:
    """Comando para confirmar una orden"""
    order_id: str


@dataclass
class CancelOrderCommand:
    """Comando para cancelar una orden"""
    order_id: str


@dataclass
class MarkOrderPickedCommand:
    """Comando para marcar orden como recogida"""
    order_id: str


@dataclass
class MarkOrderShippedCommand:
    """Comando para marcar orden como enviada"""
    order_id: str


@dataclass
class MarkOrderDeliveredCommand:
    """Comando para marcar orden como entregada"""
    order_id: str


@dataclass
class AddReservationCommand:
    """Comando para agregar reserva a una orden"""
    order_id: str
    reservation_id: str


@dataclass
class RemoveReservationCommand:
    """Comando para eliminar reserva de una orden"""
    order_id: str
    reservation_id: str


@dataclass
class RequestReturnCommand:
    """Comando para solicitar devolución de una orden"""
    order_id: str
    reason: str


@dataclass
class DeleteOrderCommand:
    """Comando para eliminar una orden"""
    order_id: str

