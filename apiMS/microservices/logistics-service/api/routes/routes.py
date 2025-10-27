"""
Rutas de la API de logística
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from ...application.commands import (
    CreateRouteCommand, StartRouteCommand, CompleteRouteCommand, CancelRouteCommand
)
from ...application.queries import (
    GetRouteByIdQuery, GetRoutesByVehicleQuery, GetRoutesByStatusQuery, GetAllRoutesQuery
)
from ..dependencies import (
    get_create_route_handler, get_start_route_handler, get_complete_route_handler,
    get_cancel_route_handler, get_route_by_id_handler,
    get_routes_by_vehicle_handler, get_routes_by_status_handler, get_all_routes_handler
)

router = APIRouter()


# ========== Schemas ==========

class StopRequest(BaseModel):
    """Request para parada"""
    orderId: str = Field(..., alias="orderId")
    priority: int = Field(default=1, ge=1)
    eta: Optional[dict] = None


class CreateRouteRequest(BaseModel):
    """Request para crear ruta"""
    stops: List[StopRequest] = Field(..., min_items=1)
    vehicleId: Optional[str] = Field(None, alias="vehicleId")


class RouteResponse(BaseModel):
    """Response de ruta"""
    id: str
    vehicleId: Optional[str]
    status: str
    stops: List[dict]
    created_at: datetime
    updated_at: datetime


# ========== Endpoints ==========

@router.post(
    "/routes",
    response_model=RouteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear ruta",
    description="Crea una nueva ruta de entrega"
)
async def create_route(
    request: CreateRouteRequest,
    handler=Depends(get_create_route_handler)
):
    """Crear nueva ruta"""
    try:
        command = CreateRouteCommand(
            stops=[stop.dict() for stop in request.stops],
            vehicle_id=request.vehicleId
        )
        
        route = await handler.handle(command)
        
        return RouteResponse(
            id=str(route.id),
            vehicleId=route.vehicle_id,
            status=route.status.value,
            stops=[stop.to_dict() for stop in route.stops],
            created_at=route.created_at,
            updated_at=route.updated_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/routes/{route_id}",
    response_model=RouteResponse,
    summary="Obtener ruta",
    description="Obtiene una ruta por ID"
)
async def get_route(
    route_id: str,
    handler=Depends(get_route_by_id_handler)
):
    """Obtener ruta por ID"""
    try:
        query = GetRouteByIdQuery(route_id=route_id)
        route = await handler.handle(query)
        
        return RouteResponse(
            id=str(route.id),
            vehicleId=route.vehicle_id,
            status=route.status.value,
            stops=[stop.to_dict() for stop in route.stops],
            created_at=route.created_at,
            updated_at=route.updated_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post(
    "/routes/{route_id}/start",
    response_model=RouteResponse,
    summary="Iniciar ruta",
    description="Inicia una ruta"
)
async def start_route(
    route_id: str,
    vehicleId: str = Field(..., alias="vehicleId"),
    handler=Depends(get_start_route_handler)
):
    """Iniciar ruta"""
    try:
        command = StartRouteCommand(route_id=route_id, vehicle_id=vehicleId)
        route = await handler.handle(command)
        
        return RouteResponse(
            id=str(route.id),
            vehicleId=route.vehicle_id,
            status=route.status.value,
            stops=[stop.to_dict() for stop in route.stops],
            created_at=route.created_at,
            updated_at=route.updated_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/routes/{route_id}/complete",
    response_model=RouteResponse,
    summary="Completar ruta",
    description="Completa una ruta"
)
async def complete_route(
    route_id: str,
    handler=Depends(get_complete_route_handler)
):
    """Completar ruta"""
    try:
        command = CompleteRouteCommand(route_id=route_id)
        route = await handler.handle(command)
        
        return RouteResponse(
            id=str(route.id),
            vehicleId=route.vehicle_id,
            status=route.status.value,
            stops=[stop.to_dict() for stop in route.stops],
            created_at=route.created_at,
            updated_at=route.updated_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/routes/{route_id}/cancel",
    response_model=RouteResponse,
    summary="Cancelar ruta",
    description="Cancela una ruta"
)
async def cancel_route(
    route_id: str,
    handler=Depends(get_cancel_route_handler)
):
    """Cancelar ruta"""
    try:
        command = CancelRouteCommand(route_id=route_id)
        route = await handler.handle(command)
        
        return RouteResponse(
            id=str(route.id),
            vehicleId=route.vehicle_id,
            status=route.status.value,
            stops=[stop.to_dict() for stop in route.stops],
            created_at=route.created_at,
            updated_at=route.updated_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/routes",
    response_model=List[RouteResponse],
    summary="Listar rutas",
    description="Lista todas las rutas"
)
async def list_routes(
    skip: int = 0,
    limit: int = 100,
    handler=Depends(get_all_routes_handler)
):
    """Listar rutas"""
    try:
        query = GetAllRoutesQuery(skip=skip, limit=limit)
        routes = await handler.handle(query)
        
        return [
            RouteResponse(
                id=str(route.id),
                vehicleId=route.vehicle_id,
                status=route.status.value,
                stops=[stop.to_dict() for stop in route.stops],
                created_at=route.created_at,
                updated_at=route.updated_at
            )
            for route in routes
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

