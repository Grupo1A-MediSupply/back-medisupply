"""
Dependencies de la API
"""
from functools import lru_cache
from fastapi import Depends
from ...infrastructure.database import get_db
from ...infrastructure.repositories import SQLAlchemyOrderRepository
from ...infrastructure.adapters.product_service_adapter import ProductServiceAdapter
from ...domain.ports import IOrderRepository
from ...application.handlers import (
    CreateOrderCommandHandler,
    UpdateOrderCommandHandler,
    ConfirmOrderCommandHandler,
    CancelOrderCommandHandler,
    MarkOrderPickedCommandHandler,
    MarkOrderShippedCommandHandler,
    MarkOrderDeliveredCommandHandler,
    AddReservationCommandHandler,
    RemoveReservationCommandHandler,
    RequestReturnCommandHandler,
    DeleteOrderCommandHandler,
    GetOrderByIdQueryHandler,
    GetOrdersByStatusQueryHandler,
    GetAllOrdersQueryHandler
)


def get_order_repository(db=Depends(get_db)) -> IOrderRepository:
    """Dependency para obtener repositorio de órdenes"""
    return SQLAlchemyOrderRepository(db)


def get_product_adapter():
    """Dependency para obtener adaptador de productos"""
    return ProductServiceAdapter()


def get_create_order_handler(
    repo=Depends(get_order_repository),
    product_adapter=Depends(get_product_adapter)
):
    """Dependency para obtener handler de crear orden"""
    return CreateOrderCommandHandler(repo, product_adapter)


def get_update_order_handler(repo=Depends(get_order_repository)):
    """Dependency para obtener handler de actualizar orden"""
    return UpdateOrderCommandHandler(repo)


def get_confirm_order_handler(repo=Depends(get_order_repository)):
    """Dependency para obtener handler de confirmar orden"""
    return ConfirmOrderCommandHandler(repo)


def get_cancel_order_handler(repo=Depends(get_order_repository)):
    """Dependency para obtener handler de cancelar orden"""
    return CancelOrderCommandHandler(repo)


def get_mark_order_picked_handler(repo=Depends(get_order_repository)):
    """Dependency para obtener handler de marcar orden como recogida"""
    return MarkOrderPickedCommandHandler(repo)


def get_mark_order_shipped_handler(repo=Depends(get_order_repository)):
    """Dependency para obtener handler de marcar orden como enviada"""
    return MarkOrderShippedCommandHandler(repo)


def get_mark_order_delivered_handler(repo=Depends(get_order_repository)):
    """Dependency para obtener handler de marcar orden como entregada"""
    return MarkOrderDeliveredCommandHandler(repo)


def get_add_reservation_handler(repo=Depends(get_order_repository)):
    """Dependency para obtener handler de agregar reserva"""
    return AddReservationCommandHandler(repo)


def get_remove_reservation_handler(repo=Depends(get_order_repository)):
    """Dependency para obtener handler de eliminar reserva"""
    return RemoveReservationCommandHandler(repo)


def get_order_by_id_handler(repo=Depends(get_order_repository)):
    """Dependency para obtener handler de obtener orden por ID"""
    return GetOrderByIdQueryHandler(repo)


def get_orders_by_status_handler(repo=Depends(get_order_repository)):
    """Dependency para obtener handler de obtener órdenes por estado"""
    return GetOrdersByStatusQueryHandler(repo)


def get_all_orders_handler(repo=Depends(get_order_repository)):
    """Dependency para obtener handler de obtener todas las órdenes"""
    return GetAllOrdersQueryHandler(repo)


def get_request_return_handler(repo=Depends(get_order_repository)):
    """Dependency para obtener handler de solicitar devolución"""
    return RequestReturnCommandHandler(repo)


def get_delete_order_handler(repo=Depends(get_order_repository)):
    """Dependency para obtener handler de eliminar orden"""
    return DeleteOrderCommandHandler(repo)
