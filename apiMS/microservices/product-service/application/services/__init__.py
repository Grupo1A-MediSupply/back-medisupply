"""
Event handlers del servicio de productos
"""
import sys
from pathlib import Path

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from ...domain.events import (
    ProductCreatedEvent,
    ProductUpdatedEvent,
    ProductDeactivatedEvent,
    StockUpdatedEvent,
    LowStockEvent
)


class ProductEventHandler:
    """Handler para eventos de producto"""
    
    async def on_product_created(self, event: ProductCreatedEvent):
        """Manejar evento de producto creado"""
        print(f"📦 [EVENT] Producto creado: {event.name} (${event.price})")
        # Aquí se podría notificar a otros servicios
        # Aquí se podría publicar a un message broker
    
    async def on_product_updated(self, event: ProductUpdatedEvent):
        """Manejar evento de producto actualizado"""
        print(f"✏️ [EVENT] Producto actualizado: {event.product_id}")
        # Aquí se podría invalidar cachés
        # Aquí se podría sincronizar con otros servicios
    
    async def on_product_deactivated(self, event: ProductDeactivatedEvent):
        """Manejar evento de producto desactivado"""
        print(f"❌ [EVENT] Producto desactivado: {event.product_id}")
        # Aquí se podría notificar a otros servicios
    
    async def on_stock_updated(self, event: StockUpdatedEvent):
        """Manejar evento de stock actualizado"""
        print(f"📊 [EVENT] Stock actualizado: Producto {event.product_id} - {event.old_stock} → {event.new_stock}")
        # Aquí se podría actualizar un sistema de inventario
    
    async def on_low_stock(self, event: LowStockEvent):
        """Manejar evento de stock bajo"""
        print(f"⚠️ [EVENT] Stock bajo: Producto {event.product_id} - Stock actual: {event.current_stock}")
        # Aquí se podría enviar una notificación
        # Aquí se podría crear una orden de reabastecimiento automática


def setup_event_handlers(event_handler: ProductEventHandler):
    """Configurar handlers de eventos"""
    from shared.domain.events import event_bus
    
    event_bus.subscribe("ProductCreatedEvent", event_handler.on_product_created)
    event_bus.subscribe("ProductUpdatedEvent", event_handler.on_product_updated)
    event_bus.subscribe("ProductDeactivatedEvent", event_handler.on_product_deactivated)
    event_bus.subscribe("StockUpdatedEvent", event_handler.on_stock_updated)
    event_bus.subscribe("LowStockEvent", event_handler.on_low_stock)

