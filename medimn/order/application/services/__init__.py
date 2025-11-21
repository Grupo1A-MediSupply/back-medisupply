"""
Servicios de aplicación para órdenes
"""
import sys
from pathlib import Path

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from shared.domain.events import event_bus
from ...domain.events import (
    OrderCreatedEvent, OrderConfirmedEvent, OrderCancelledEvent,
    OrderShippedEvent, OrderDeliveredEvent
)


class OrderEventHandler:
    """Event Handler para eventos de órdenes"""
    
    async def handle_order_created(self, event: OrderCreatedEvent):
        """Manejar evento de orden creada"""
        print(f"📦 Nueva orden creada: {event.order_id}")
        # Aquí se podría notificar a otros servicios, enviar correos, etc.
    
    async def handle_order_confirmed(self, event: OrderConfirmedEvent):
        """Manejar evento de orden confirmada"""
        print(f"✅ Orden confirmada: {event.order_id}")
        # Aquí se podría iniciar procesos de reserva de inventario, etc.
    
    async def handle_order_cancelled(self, event: OrderCancelledEvent):
        """Manejar evento de orden cancelada"""
        print(f"❌ Orden cancelada: {event.order_id}")
        # Aquí se podría liberar inventario reservado, etc.
    
    async def handle_order_shipped(self, event: OrderShippedEvent):
        """Manejar evento de orden enviada"""
        print(f"🚚 Orden enviada: {event.order_id}")
        # Aquí se podría notificar al cliente, actualizar tracking, etc.
    
    async def handle_order_delivered(self, event: OrderDeliveredEvent):
        """Manejar evento de orden entregada"""
        print(f"🎉 Orden entregada: {event.order_id}")
        # Aquí se podría completar el pedido, generar factura, etc.


def setup_event_handlers(event_handler: OrderEventHandler):
    """Configurar event handlers"""
    event_bus.subscribe(OrderCreatedEvent, event_handler.handle_order_created)
    event_bus.subscribe(OrderConfirmedEvent, event_handler.handle_order_confirmed)
    event_bus.subscribe(OrderCancelledEvent, event_handler.handle_order_cancelled)
    event_bus.subscribe(OrderShippedEvent, event_handler.handle_order_shipped)
    event_bus.subscribe(OrderDeliveredEvent, event_handler.handle_order_delivered)

