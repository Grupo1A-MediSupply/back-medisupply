"""
Eventos de dominio para órdenes
"""
import sys
from pathlib import Path

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from shared.domain.events import DomainEvent


class OrderCreatedEvent(DomainEvent):
    """Evento cuando se crea un pedido"""
    
    def __init__(self, order_id: str, user_id: str):
        super().__init__()
        self.order_id = order_id
        self.user_id = user_id


class OrderConfirmedEvent(DomainEvent):
    """Evento cuando se confirma un pedido"""
    
    def __init__(self, order_id: str):
        super().__init__()
        self.order_id = order_id


class OrderCancelledEvent(DomainEvent):
    """Evento cuando se cancela un pedido"""
    
    def __init__(self, order_id: str):
        super().__init__()
        self.order_id = order_id


class OrderShippedEvent(DomainEvent):
    """Evento cuando se envía un pedido"""
    
    def __init__(self, order_id: str):
        super().__init__()
        self.order_id = order_id


class OrderDeliveredEvent(DomainEvent):
    """Evento cuando se entrega un pedido"""
    
    def __init__(self, order_id: str):
        super().__init__()
        self.order_id = order_id

