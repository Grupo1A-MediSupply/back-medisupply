"""
Handlers para comandos y queries
"""
import sys
from pathlib import Path

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from shared.domain.value_objects import EntityId
from shared.domain.events import event_bus
from ..commands import (
    CreateOrderCommand, UpdateOrderCommand, ConfirmOrderCommand,
    CancelOrderCommand, MarkOrderPickedCommand, MarkOrderShippedCommand,
    MarkOrderDeliveredCommand, AddReservationCommand, RemoveReservationCommand,
    RequestReturnCommand, DeleteOrderCommand
)
from ..queries import (
    GetOrderByIdQuery, GetOrdersByStatusQuery, GetAllOrdersQuery
)
from ...domain.entities import Order, OrderItem, ETA, OrderStatus
from ...domain.events import (
    OrderCreatedEvent, OrderConfirmedEvent, OrderCancelledEvent,
    OrderShippedEvent, OrderDeliveredEvent
)
from ...domain.ports import IOrderRepository


class CreateOrderCommandHandler:
    """Handler para el comando CreateOrder"""
    
    def __init__(
        self, 
        order_repository: IOrderRepository,
        product_adapter=None  # ProductServiceAdapter
    ):
        self.order_repository = order_repository
        self.product_adapter = product_adapter
    
    async def handle(self, command: CreateOrderCommand) -> Order:
        """Manejar comando de creación de orden"""
        # Validar productos con el servicio de productos (si el adaptador está disponible)
        if self.product_adapter:
            try:
                sku_ids = [item["skuId"] for item in command.items]
                await self.product_adapter.validate_products(sku_ids)
            except ValueError as e:
                raise ValueError(f"Error al validar productos: {str(e)}")
        
        # Convertir items
        order_items = [
            OrderItem(
                sku_id=item["skuId"],
                qty=item["qty"],
                price=item["price"]
            )
            for item in command.items
        ]
        
        # Convertir ETA
        eta = None
        if command.eta:
            from datetime import datetime
            eta = ETA(
                date=command.eta["date"],
                window_minutes=command.eta["windowMinutes"]
            )
        
        # Crear orden
        order = Order.create(
            items=order_items,
            reservations=command.reservations,
            eta=eta,
            status=OrderStatus.PLACED,
            client_id=command.client_id,
            vendor_id=command.vendor_id,
            delivery_address=command.delivery_address,
            delivery_date=command.delivery_date,
            contact_name=command.contact_name,
            contact_phone=command.contact_phone,
            notes=command.notes,
            route_id=command.route_id
        )
        
        # Guardar orden
        order = await self.order_repository.save(order)
        
        # Publicar eventos
        order._record_event(OrderCreatedEvent(
            order_id=str(order.id),
            user_id=""  # En producción, obtener del contexto de autenticación
        ))
        
        for event in order.get_domain_events():
            await event_bus.publish(event)
        
        order.clear_domain_events()
        
        return order


class UpdateOrderCommandHandler:
    """Handler para el comando UpdateOrder"""
    
    def __init__(self, order_repository: IOrderRepository):
        self.order_repository = order_repository
    
    async def handle(self, command: UpdateOrderCommand) -> Order:
        """Manejar comando de actualización de orden"""
        # Buscar orden
        order = await self.order_repository.find_by_id(EntityId(command.order_id))
        if not order:
            raise ValueError(f"Orden {command.order_id} no encontrada")
        
        # Actualizar items si se proporcionan
        if command.items:
            order_items = [
                OrderItem(
                    sku_id=item["skuId"],
                    qty=item["qty"],
                    price=item["price"]
                )
                for item in command.items
            ]
            order._items = order_items
            order._totals = order._calculate_totals()
        
        # Actualizar ETA si se proporciona
        if command.eta:
            from datetime import datetime
            eta = ETA(
                date=command.eta["date"],
                window_minutes=command.eta["windowMinutes"]
            )
            order.set_eta(eta)
        
        # Actualizar status si se proporciona
        if command.status:
            status_enum = OrderStatus(command.status)
            if status_enum == OrderStatus.CONFIRMED:
                order.confirm()
            elif status_enum == OrderStatus.CANCELLED:
                order.cancel()
            elif status_enum == OrderStatus.PICKED:
                order.mark_as_picked()
            elif status_enum == OrderStatus.SHIPPED:
                order.mark_as_shipped()
            elif status_enum == OrderStatus.DELIVERED:
                order.mark_as_delivered()
        
        # Actualizar información de entrega
        order.update_delivery_info(
            delivery_address=command.delivery_address,
            delivery_date=command.delivery_date,
            contact_name=command.contact_name,
            contact_phone=command.contact_phone,
            notes=command.notes,
            route_id=command.route_id
        )
        
        # Guardar orden
        order = await self.order_repository.save(order)
        
        return order


class ConfirmOrderCommandHandler:
    """Handler para el comando ConfirmOrder"""
    
    def __init__(self, order_repository: IOrderRepository):
        self.order_repository = order_repository
    
    async def handle(self, command: ConfirmOrderCommand) -> Order:
        """Manejar comando de confirmación de orden"""
        order = await self.order_repository.find_by_id(EntityId(command.order_id))
        if not order:
            raise ValueError(f"Orden {command.order_id} no encontrada")
        
        order.confirm()
        
        # Publicar eventos
        order._record_event(OrderConfirmedEvent(order_id=str(order.id)))
        
        for event in order.get_domain_events():
            await event_bus.publish(event)
        
        order.clear_domain_events()
        
        order = await self.order_repository.save(order)
        
        return order


class CancelOrderCommandHandler:
    """Handler para el comando CancelOrder"""
    
    def __init__(self, order_repository: IOrderRepository):
        self.order_repository = order_repository
    
    async def handle(self, command: CancelOrderCommand) -> Order:
        """Manejar comando de cancelación de orden"""
        order = await self.order_repository.find_by_id(EntityId(command.order_id))
        if not order:
            raise ValueError(f"Orden {command.order_id} no encontrada")
        
        order.cancel()
        
        # Publicar eventos
        order._record_event(OrderCancelledEvent(order_id=str(order.id)))
        
        for event in order.get_domain_events():
            await event_bus.publish(event)
        
        order.clear_domain_events()
        
        order = await self.order_repository.save(order)
        
        return order


class MarkOrderPickedCommandHandler:
    """Handler para el comando MarkOrderPicked"""
    
    def __init__(self, order_repository: IOrderRepository):
        self.order_repository = order_repository
    
    async def handle(self, command: MarkOrderPickedCommand) -> Order:
        """Manejar comando de marcar orden como recogida"""
        order = await self.order_repository.find_by_id(EntityId(command.order_id))
        if not order:
            raise ValueError(f"Orden {command.order_id} no encontrada")
        
        order.mark_as_picked()
        order = await self.order_repository.save(order)
        
        return order


class MarkOrderShippedCommandHandler:
    """Handler para el comando MarkOrderShipped"""
    
    def __init__(self, order_repository: IOrderRepository):
        self.order_repository = order_repository
    
    async def handle(self, command: MarkOrderShippedCommand) -> Order:
        """Manejar comando de marcar orden como enviada"""
        order = await self.order_repository.find_by_id(EntityId(command.order_id))
        if not order:
            raise ValueError(f"Orden {command.order_id} no encontrada")
        
        order.mark_as_shipped()
        
        # Publicar eventos
        order._record_event(OrderShippedEvent(order_id=str(order.id)))
        
        for event in order.get_domain_events():
            await event_bus.publish(event)
        
        order.clear_domain_events()
        
        order = await self.order_repository.save(order)
        
        return order


class MarkOrderDeliveredCommandHandler:
    """Handler para el comando MarkOrderDelivered"""
    
    def __init__(self, order_repository: IOrderRepository):
        self.order_repository = order_repository
    
    async def handle(self, command: MarkOrderDeliveredCommand) -> Order:
        """Manejar comando de marcar orden como entregada"""
        order = await self.order_repository.find_by_id(EntityId(command.order_id))
        if not order:
            raise ValueError(f"Orden {command.order_id} no encontrada")
        
        order.mark_as_delivered()
        
        # Publicar eventos
        order._record_event(OrderDeliveredEvent(order_id=str(order.id)))
        
        for event in order.get_domain_events():
            await event_bus.publish(event)
        
        order.clear_domain_events()
        
        order = await self.order_repository.save(order)
        
        return order


class AddReservationCommandHandler:
    """Handler para el comando AddReservation"""
    
    def __init__(self, order_repository: IOrderRepository):
        self.order_repository = order_repository
    
    async def handle(self, command: AddReservationCommand) -> Order:
        """Manejar comando de agregar reserva"""
        order = await self.order_repository.find_by_id(EntityId(command.order_id))
        if not order:
            raise ValueError(f"Orden {command.order_id} no encontrada")
        
        order.add_reservation(command.reservation_id)
        order = await self.order_repository.save(order)
        
        return order


class RemoveReservationCommandHandler:
    """Handler para el comando RemoveReservation"""
    
    def __init__(self, order_repository: IOrderRepository):
        self.order_repository = order_repository
    
    async def handle(self, command: RemoveReservationCommand) -> Order:
        """Manejar comando de eliminar reserva"""
        order = await self.order_repository.find_by_id(EntityId(command.order_id))
        if not order:
            raise ValueError(f"Orden {command.order_id} no encontrada")
        
        order.remove_reservation(command.reservation_id)
        order = await self.order_repository.save(order)
        
        return order


class RequestReturnCommandHandler:
    """Handler para el comando RequestReturn"""
    
    def __init__(self, order_repository: IOrderRepository):
        self.order_repository = order_repository
    
    async def handle(self, command: RequestReturnCommand) -> Order:
        """Manejar comando de solicitud de devolución"""
        order = await self.order_repository.find_by_id(EntityId(command.order_id))
        if not order:
            raise ValueError(f"Orden {command.order_id} no encontrada")
        
        order.request_return(command.reason)
        order = await self.order_repository.save(order)
        
        return order


class DeleteOrderCommandHandler:
    """Handler para el comando DeleteOrder"""
    
    def __init__(self, order_repository: IOrderRepository):
        self.order_repository = order_repository
    
    async def handle(self, command: DeleteOrderCommand) -> bool:
        """Manejar comando de eliminación de orden"""
        deleted = await self.order_repository.delete(EntityId(command.order_id))
        if not deleted:
            raise ValueError(f"Orden {command.order_id} no encontrada")
        
        return True


# ========== Query Handlers ==========

class GetOrderByIdQueryHandler:
    """Handler para la query GetOrderById"""
    
    def __init__(self, order_repository: IOrderRepository):
        self.order_repository = order_repository
    
    async def handle(self, query: GetOrderByIdQuery) -> Order:
        """Manejar query de obtener orden por ID"""
        order = await self.order_repository.find_by_id(EntityId(query.order_id))
        if not order:
            raise ValueError(f"Orden {query.order_id} no encontrada")
        
        return order


class GetOrdersByStatusQueryHandler:
    """Handler para la query GetOrdersByStatus"""
    
    def __init__(self, order_repository: IOrderRepository):
        self.order_repository = order_repository
    
    async def handle(self, query: GetOrdersByStatusQuery) -> list:
        """Manejar query de obtener órdenes por estado"""
        status_enum = OrderStatus(query.status)
        orders = await self.order_repository.find_by_status(status_enum)
        return orders


class GetAllOrdersQueryHandler:
    """Handler para la query GetAllOrders"""
    
    def __init__(self, order_repository: IOrderRepository):
        self.order_repository = order_repository
    
    async def handle(self, query: GetAllOrdersQuery) -> list:
        """Manejar query de obtener todas las órdenes"""
        status_enum = None
        if query.status:
            status_enum = OrderStatus(query.status)
        orders = await self.order_repository.find_all(skip=query.skip, limit=query.limit, status=status_enum)
        return orders

