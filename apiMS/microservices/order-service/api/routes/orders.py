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
    MarkOrderDeliveredCommand, AddReservationCommand, RemoveReservationCommand,
    RequestReturnCommand, DeleteOrderCommand
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
    get_all_orders_handler,
    get_request_return_handler,
    get_delete_order_handler
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
    clientId: Optional[str] = None
    vendorId: Optional[str] = None
    deliveryAddress: Optional[str] = None
    deliveryDate: Optional[datetime] = None
    contactName: Optional[str] = None
    contactPhone: Optional[str] = None
    notes: Optional[str] = None
    routeId: Optional[str] = None


class UpdateOrderRequest(BaseModel):
    """Request para actualizar orden"""
    items: Optional[List[OrderItemRequest]] = None
    eta: Optional[ETARequest] = None
    status: Optional[str] = None
    deliveryAddress: Optional[str] = None
    deliveryDate: Optional[datetime] = None
    contactName: Optional[str] = None
    contactPhone: Optional[str] = None
    notes: Optional[str] = None
    routeId: Optional[str] = None


class RequestReturnRequest(BaseModel):
    """Request para solicitar devolución"""
    reason: str = Field(..., min_length=1)


class OrderResponse(BaseModel):
    """Response de orden"""
    id: Optional[str] = None
    _id: Optional[str] = None  # Alias según especificación
    orderNumber: Optional[str] = None
    clientId: Optional[str] = None
    vendorId: Optional[str] = None
    products: Optional[List[dict]] = None  # Alias para items según especificación
    items: Optional[List[dict]] = None
    status: str
    deliveryAddress: Optional[str] = None
    deliveryDate: Optional[datetime] = None
    contactName: Optional[str] = None
    contactPhone: Optional[str] = None
    notes: Optional[str] = None
    routeId: Optional[str] = None
    returnRequested: bool = False
    returnReason: Optional[str] = None
    returnStatus: Optional[str] = None
    reservations: Optional[List[str]] = None
    eta: Optional[dict] = None
    totals: Optional[dict] = None
    totalAmount: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    createdAt: Optional[str] = None  # Alias según especificación
    updatedAt: Optional[str] = None  # Alias según especificación


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
            eta=request.eta.dict() if request.eta else None,
            client_id=request.clientId,
            vendor_id=request.vendorId,
            delivery_address=request.deliveryAddress,
            delivery_date=request.deliveryDate,
            contact_name=request.contactName,
            contact_phone=request.contactPhone,
            notes=request.notes,
            route_id=request.routeId
        )
        
        order = await handler.handle(command)
        
        return OrderResponse(
            id=str(order.id),
            _id=str(order.id),
            orderNumber=order.order_number,
            clientId=order.client_id,
            vendorId=order.vendor_id,
            products=[item.to_dict() for item in order.items],
            items=[item.to_dict() for item in order.items],
            status=order.status.value,
            deliveryAddress=order.delivery_address,
            deliveryDate=order.delivery_date,
            contactName=order.contact_name,
            contactPhone=order.contact_phone,
            notes=order.notes,
            routeId=order.route_id,
            returnRequested=order.return_requested,
            returnReason=order.return_reason,
            returnStatus=order.return_status.value if order.return_status else None,
            reservations=order.reservations,
            eta=order.eta.to_dict() if order.eta else None,
            totals=order.totals,
            totalAmount=order.total_amount,
            created_at=order.created_at,
            updated_at=order.updated_at,
            createdAt=order.created_at.isoformat() if order.created_at else None,
            updatedAt=order.updated_at.isoformat() if order.updated_at else None
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
            _id=str(order.id),
            orderNumber=order.order_number,
            clientId=order.client_id,
            vendorId=order.vendor_id,
            products=[item.to_dict() for item in order.items],
            items=[item.to_dict() for item in order.items],
            status=order.status.value,
            deliveryAddress=order.delivery_address,
            deliveryDate=order.delivery_date,
            contactName=order.contact_name,
            contactPhone=order.contact_phone,
            notes=order.notes,
            routeId=order.route_id,
            returnRequested=order.return_requested,
            returnReason=order.return_reason,
            returnStatus=order.return_status.value if order.return_status else None,
            reservations=order.reservations,
            eta=order.eta.to_dict() if order.eta else None,
            totals=order.totals,
            totalAmount=order.total_amount,
            created_at=order.created_at,
            updated_at=order.updated_at,
            createdAt=order.created_at.isoformat() if order.created_at else None,
            updatedAt=order.updated_at.isoformat() if order.updated_at else None
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
    status: Optional[str] = None,
    handler=Depends(get_all_orders_handler)
):
    """Listar órdenes"""
    try:
        query = GetAllOrdersQuery(skip=skip, limit=limit, status=status)
        orders = await handler.handle(query)
        
        return [
            OrderResponse(
                id=str(order.id),
                _id=str(order.id),
                orderNumber=order.order_number,
                clientId=order.client_id,
                vendorId=order.vendor_id,
                products=[item.to_dict() for item in order.items],
                items=[item.to_dict() for item in order.items],
                status=order.status.value,
                deliveryAddress=order.delivery_address,
                deliveryDate=order.delivery_date,
                contactName=order.contact_name,
                contactPhone=order.contact_phone,
                notes=order.notes,
                routeId=order.route_id,
                returnRequested=order.return_requested,
                returnReason=order.return_reason,
                returnStatus=order.return_status.value if order.return_status else None,
                reservations=order.reservations,
                eta=order.eta.to_dict() if order.eta else None,
                totals=order.totals,
                totalAmount=order.total_amount,
                created_at=order.created_at,
                updated_at=order.updated_at,
                createdAt=order.created_at.isoformat() if order.created_at else None,
                updatedAt=order.updated_at.isoformat() if order.updated_at else None
            )
            for order in orders
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put(
    "/orders/{order_id}",
    response_model=OrderResponse,
    summary="Actualizar orden",
    description="Actualiza una orden existente"
)
async def update_order(
    order_id: str,
    request: UpdateOrderRequest,
    handler=Depends(get_update_order_handler)
):
    """Actualizar orden"""
    try:
        eta_dict = None
        if request.eta:
            eta_dict = request.eta.dict()
        
        command = UpdateOrderCommand(
            order_id=order_id,
            items=[item.dict() for item in request.items] if request.items else None,
            eta=eta_dict,
            status=request.status,
            delivery_address=request.deliveryAddress,
            delivery_date=request.deliveryDate,
            contact_name=request.contactName,
            contact_phone=request.contactPhone,
            notes=request.notes,
            route_id=request.routeId
        )
        
        order = await handler.handle(command)
        
        return OrderResponse(
            id=str(order.id),
            _id=str(order.id),
            orderNumber=order.order_number,
            clientId=order.client_id,
            vendorId=order.vendor_id,
            products=[item.to_dict() for item in order.items],
            items=[item.to_dict() for item in order.items],
            status=order.status.value,
            deliveryAddress=order.delivery_address,
            deliveryDate=order.delivery_date,
            contactName=order.contact_name,
            contactPhone=order.contact_phone,
            notes=order.notes,
            routeId=order.route_id,
            returnRequested=order.return_requested,
            returnReason=order.return_reason,
            returnStatus=order.return_status.value if order.return_status else None,
            reservations=order.reservations,
            eta=order.eta.to_dict() if order.eta else None,
            totals=order.totals,
            totalAmount=order.total_amount,
            created_at=order.created_at,
            updated_at=order.updated_at,
            createdAt=order.created_at.isoformat() if order.created_at else None,
            updatedAt=order.updated_at.isoformat() if order.updated_at else None
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete(
    "/orders/{order_id}",
    response_model=dict,
    summary="Eliminar orden",
    description="Elimina una orden"
)
async def delete_order(
    order_id: str,
    handler=Depends(get_delete_order_handler)
):
    """Eliminar orden"""
    try:
        command = DeleteOrderCommand(order_id=order_id)
        await handler.handle(command)
        
        return {"message": "Orden eliminada exitosamente"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/orders/{order_id}/return",
    response_model=OrderResponse,
    summary="Solicitar devolución",
    description="Solicita la devolución de una orden entregada"
)
async def request_return(
    order_id: str,
    request: RequestReturnRequest,
    handler=Depends(get_request_return_handler)
):
    """Solicitar devolución de orden"""
    try:
        command = RequestReturnCommand(
            order_id=order_id,
            reason=request.reason
        )
        
        order = await handler.handle(command)
        
        return OrderResponse(
            id=str(order.id),
            _id=str(order.id),
            orderNumber=order.order_number,
            clientId=order.client_id,
            vendorId=order.vendor_id,
            products=[item.to_dict() for item in order.items],
            items=[item.to_dict() for item in order.items],
            status=order.status.value,
            deliveryAddress=order.delivery_address,
            deliveryDate=order.delivery_date,
            contactName=order.contact_name,
            contactPhone=order.contact_phone,
            notes=order.notes,
            routeId=order.route_id,
            returnRequested=order.return_requested,
            returnReason=order.return_reason,
            returnStatus=order.return_status.value if order.return_status else None,
            reservations=order.reservations,
            eta=order.eta.to_dict() if order.eta else None,
            totals=order.totals,
            totalAmount=order.total_amount,
            created_at=order.created_at,
            updated_at=order.updated_at,
            createdAt=order.created_at.isoformat() if order.created_at else None,
            updatedAt=order.updated_at.isoformat() if order.updated_at else None
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

