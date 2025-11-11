"""
Rutas de la API de órdenes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from ...application.commands import (
    CreateOrderCommand, UpdateOrderCommand, ConfirmOrderCommand,
    CancelOrderCommand, MarkOrderPickedCommand, MarkOrderShippedCommand,
    MarkOrderDeliveredCommand, AddReservationCommand, RemoveReservationCommand
)
from ...application.queries import (
    GetOrderByIdQuery, GetOrdersByStatusQuery, GetAllOrdersQuery
)
from ..dependencies import (
    get_create_order_handler,
    get_update_order_handler,
    get_confirm_order_handler,
    get_cancel_order_handler,
    get_mark_order_picked_handler,
    get_mark_order_shipped_handler,
    get_mark_order_delivered_handler,
    get_add_reservation_handler,
    get_remove_reservation_handler,
    get_order_by_id_handler,
    get_orders_by_status_handler,
    get_all_orders_handler
)

router = APIRouter()


# ========== Schemas ==========

class OrderItemRequest(BaseModel):
    """Request para artículo de orden"""
    skuId: str = Field(..., alias="skuId")
    qty: int = Field(..., ge=1)
    price: float = Field(..., ge=0)


class ETARequest(BaseModel):
    """Request para ETA"""
    date: datetime
    windowMinutes: int = Field(..., alias="windowMinutes", ge=0)


class CreateOrderRequest(BaseModel):
    """Request para crear orden"""
    items: List[OrderItemRequest] = Field(..., min_items=1)
    eta: Optional[ETARequest] = None


class UpdateOrderRequest(BaseModel):
    """Request para actualizar orden"""
    items: Optional[List[OrderItemRequest]] = None
    eta: Optional[ETARequest] = None


class OrderResponse(BaseModel):
    """Response de orden"""
    id: str
    status: str
    items: List[dict]
    reservations: List[str]
    eta: Optional[dict] = None
    totals: dict
    created_at: datetime
    updated_at: datetime


# ========== Endpoints ==========

@router.post(
    "/orders",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear orden",
    description="Crea una nueva orden"
)
async def create_order(
    request: CreateOrderRequest,
    handler=Depends(get_create_order_handler)
):
    """Crear nueva orden"""
    try:
        command = CreateOrderCommand(
            items=[item.dict() for item in request.items],
            eta=request.eta.dict() if request.eta else None
        )
        
        order = await handler.handle(command)
        
        return OrderResponse(
            id=str(order.id),
            status=order.status.value,
            items=[item.to_dict() for item in order.items],
            reservations=order.reservations,
            eta=order.eta.to_dict() if order.eta else None,
            totals=order.totals,
            created_at=order.created_at,
            updated_at=order.updated_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/orders/{order_id}",
    response_model=OrderResponse,
    summary="Obtener orden",
    description="Obtiene una orden por ID"
)
async def get_order(
    order_id: str,
    handler=Depends(get_order_by_id_handler)
):
    """Obtener orden por ID"""
    try:
        query = GetOrderByIdQuery(order_id=order_id)
        order = await handler.handle(query)
        
        return OrderResponse(
            id=str(order.id),
            status=order.status.value,
            items=[item.to_dict() for item in order.items],
            reservations=order.reservations,
            eta=order.eta.to_dict() if order.eta else None,
            totals=order.totals,
            created_at=order.created_at,
            updated_at=order.updated_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get(
    "/orders",
    response_model=List[OrderResponse],
    summary="Listar órdenes",
    description="Lista todas las órdenes"
)
async def list_orders(
    skip: int = 0,
    limit: int = 100,
    handler=Depends(get_all_orders_handler)
):
    """Listar órdenes"""
    try:
        query = GetAllOrdersQuery(skip=skip, limit=limit)
        orders = await handler.handle(query)
        
        return [
            OrderResponse(
                id=str(order.id),
                status=order.status.value,
                items=[item.to_dict() for item in order.items],
                reservations=order.reservations,
                eta=order.eta.to_dict() if order.eta else None,
                totals=order.totals,
                created_at=order.created_at,
                updated_at=order.updated_at
            )
            for order in orders
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

