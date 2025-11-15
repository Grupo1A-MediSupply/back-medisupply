"""
Rutas de la API de logística
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from ...application.commands import (
    CreateRouteCommand, StartRouteCommand, CompleteRouteCommand, CancelRouteCommand,
    UpdateRouteCommand, DeleteRouteCommand, GenerateOptimalRouteCommand
)
from ...application.queries import (
    GetRouteByIdQuery, GetRoutesByVehicleQuery, GetRoutesByStatusQuery, GetAllRoutesQuery
)
from ..dependencies import (
    get_create_route_handler, get_start_route_handler, get_complete_route_handler,
    get_cancel_route_handler, get_update_route_handler, get_delete_route_handler,
    get_generate_optimal_route_handler, get_route_by_id_handler,
    get_routes_by_vehicle_handler, get_routes_by_status_handler, get_all_routes_handler
)

router = APIRouter()


# ========== Schemas ==========

class StopRequest(BaseModel):
    """Request para parada"""
    orderId: str
    priority: int = Field(default=1, ge=1)
    eta: Optional[dict] = None
    
    class Config:
        populate_by_name = True


class CreateRouteRequest(BaseModel):
    """Request para crear ruta"""
    stops: List[StopRequest] = Field(..., min_length=1)
    vehicleId: Optional[str] = None
    vendorId: Optional[str] = None
    vehicleType: Optional[str] = None
    driverName: Optional[str] = None
    driverPhone: Optional[str] = None
    estimatedDistance: Optional[float] = None
    estimatedDuration: Optional[int] = None
    estimatedFuel: Optional[float] = None
    
    class Config:
        populate_by_name = True


class StartRouteRequest(BaseModel):
    """Request para iniciar ruta"""
    vehicleId: str
    
    class Config:
        populate_by_name = True


class UpdateRouteRequest(BaseModel):
    """Request para actualizar ruta"""
    status: Optional[str] = None
    progress: Optional[float] = Field(None, ge=0, le=100)
    actualDistance: Optional[float] = None
    actualDuration: Optional[int] = None
    actualFuel: Optional[float] = None
    endTime: Optional[datetime] = None


class GenerateOptimalRouteRequest(BaseModel):
    """Request para generar ruta óptima"""
    orderIds: List[str] = Field(..., min_items=1)
    vehicleType: Optional[str] = None


class RouteResponse(BaseModel):
    """Response de ruta"""
    id: Optional[str] = None
    _id: Optional[str] = None  # Alias según especificación
    routeNumber: Optional[str] = None
    vendorId: Optional[str] = None
    vehicleId: Optional[str] = None
    vehicleType: Optional[str] = None
    driverName: Optional[str] = None
    driverPhone: Optional[str] = None
    stops: List[dict]
    status: str
    startTime: Optional[datetime] = None
    endTime: Optional[datetime] = None
    estimatedDistance: Optional[float] = None
    estimatedDuration: Optional[int] = None
    estimatedFuel: Optional[float] = None
    actualDistance: Optional[float] = None
    actualDuration: Optional[int] = None
    actualFuel: Optional[float] = None
    progress: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    createdAt: Optional[str] = None  # Alias según especificación
    updatedAt: Optional[str] = None  # Alias según especificación


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
            vehicle_id=request.vehicleId,
            vendor_id=request.vendorId,
            vehicle_type=request.vehicleType,
            driver_name=request.driverName,
            driver_phone=request.driverPhone,
            estimated_distance=request.estimatedDistance,
            estimated_duration=request.estimatedDuration,
            estimated_fuel=request.estimatedFuel
        )
        
        route = await handler.handle(command)
        
        return RouteResponse(
            id=str(route.id),
            _id=str(route.id),
            routeNumber=route.route_number,
            vendorId=route.vendor_id,
            vehicleId=route.vehicle_id,
            vehicleType=route.vehicle_type,
            driverName=route.driver_name,
            driverPhone=route.driver_phone,
            stops=[stop.to_dict() for stop in route.stops],
            status=route.status.value,
            startTime=route.start_time,
            endTime=route.end_time,
            estimatedDistance=route.estimated_distance,
            estimatedDuration=route.estimated_duration,
            estimatedFuel=route.estimated_fuel,
            actualDistance=route.actual_distance,
            actualDuration=route.actual_duration,
            actualFuel=route.actual_fuel,
            progress=route.progress,
            created_at=route.created_at,
            updated_at=route.updated_at,
            createdAt=route.created_at.isoformat() if route.created_at else None,
            updatedAt=route.updated_at.isoformat() if route.updated_at else None
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
            _id=str(route.id),
            routeNumber=route.route_number,
            vendorId=route.vendor_id,
            vehicleId=route.vehicle_id,
            vehicleType=route.vehicle_type,
            driverName=route.driver_name,
            driverPhone=route.driver_phone,
            stops=[stop.to_dict() for stop in route.stops],
            status=route.status.value,
            startTime=route.start_time,
            endTime=route.end_time,
            estimatedDistance=route.estimated_distance,
            estimatedDuration=route.estimated_duration,
            estimatedFuel=route.estimated_fuel,
            actualDistance=route.actual_distance,
            actualDuration=route.actual_duration,
            actualFuel=route.actual_fuel,
            progress=route.progress,
            created_at=route.created_at,
            updated_at=route.updated_at,
            createdAt=route.created_at.isoformat() if route.created_at else None,
            updatedAt=route.updated_at.isoformat() if route.updated_at else None
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
    request: StartRouteRequest,
    handler=Depends(get_start_route_handler)
):
    """Iniciar ruta"""
    try:
        command = StartRouteCommand(route_id=route_id, vehicle_id=request.vehicleId)
        route = await handler.handle(command)
        
        return RouteResponse(
            id=str(route.id),
            _id=str(route.id),
            routeNumber=route.route_number,
            vendorId=route.vendor_id,
            vehicleId=route.vehicle_id,
            vehicleType=route.vehicle_type,
            driverName=route.driver_name,
            driverPhone=route.driver_phone,
            stops=[stop.to_dict() for stop in route.stops],
            status=route.status.value,
            startTime=route.start_time,
            endTime=route.end_time,
            estimatedDistance=route.estimated_distance,
            estimatedDuration=route.estimated_duration,
            estimatedFuel=route.estimated_fuel,
            actualDistance=route.actual_distance,
            actualDuration=route.actual_duration,
            actualFuel=route.actual_fuel,
            progress=route.progress,
            created_at=route.created_at,
            updated_at=route.updated_at,
            createdAt=route.created_at.isoformat() if route.created_at else None,
            updatedAt=route.updated_at.isoformat() if route.updated_at else None
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
            _id=str(route.id),
            routeNumber=route.route_number,
            vendorId=route.vendor_id,
            vehicleId=route.vehicle_id,
            vehicleType=route.vehicle_type,
            driverName=route.driver_name,
            driverPhone=route.driver_phone,
            stops=[stop.to_dict() for stop in route.stops],
            status=route.status.value,
            startTime=route.start_time,
            endTime=route.end_time,
            estimatedDistance=route.estimated_distance,
            estimatedDuration=route.estimated_duration,
            estimatedFuel=route.estimated_fuel,
            actualDistance=route.actual_distance,
            actualDuration=route.actual_duration,
            actualFuel=route.actual_fuel,
            progress=route.progress,
            created_at=route.created_at,
            updated_at=route.updated_at,
            createdAt=route.created_at.isoformat() if route.created_at else None,
            updatedAt=route.updated_at.isoformat() if route.updated_at else None
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
            _id=str(route.id),
            routeNumber=route.route_number,
            vendorId=route.vendor_id,
            vehicleId=route.vehicle_id,
            vehicleType=route.vehicle_type,
            driverName=route.driver_name,
            driverPhone=route.driver_phone,
            stops=[stop.to_dict() for stop in route.stops],
            status=route.status.value,
            startTime=route.start_time,
            endTime=route.end_time,
            estimatedDistance=route.estimated_distance,
            estimatedDuration=route.estimated_duration,
            estimatedFuel=route.estimated_fuel,
            actualDistance=route.actual_distance,
            actualDuration=route.actual_duration,
            actualFuel=route.actual_fuel,
            progress=route.progress,
            created_at=route.created_at,
            updated_at=route.updated_at,
            createdAt=route.created_at.isoformat() if route.created_at else None,
            updatedAt=route.updated_at.isoformat() if route.updated_at else None
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
    status: Optional[str] = None,
    handler=Depends(get_all_routes_handler)
):
    """Listar rutas"""
    try:
        query = GetAllRoutesQuery(skip=skip, limit=limit, status=status)
        routes = await handler.handle(query)
        
        return [
            RouteResponse(
                id=str(route.id),
                _id=str(route.id),
                routeNumber=route.route_number,
                vendorId=route.vendor_id,
                vehicleId=route.vehicle_id,
                vehicleType=route.vehicle_type,
                driverName=route.driver_name,
                driverPhone=route.driver_phone,
                stops=[stop.to_dict() for stop in route.stops],
                status=route.status.value,
                startTime=route.start_time,
                endTime=route.end_time,
                estimatedDistance=route.estimated_distance,
                estimatedDuration=route.estimated_duration,
                estimatedFuel=route.estimated_fuel,
                actualDistance=route.actual_distance,
                actualDuration=route.actual_duration,
                actualFuel=route.actual_fuel,
                progress=route.progress,
                created_at=route.created_at,
                updated_at=route.updated_at,
                createdAt=route.created_at.isoformat() if route.created_at else None,
                updatedAt=route.updated_at.isoformat() if route.updated_at else None
            )
            for route in routes
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put(
    "/routes/{route_id}",
    response_model=RouteResponse,
    summary="Actualizar ruta",
    description="Actualiza una ruta existente"
)
async def update_route(
    route_id: str,
    request: UpdateRouteRequest,
    handler=Depends(get_update_route_handler)
):
    """Actualizar ruta"""
    try:
        command = UpdateRouteCommand(
            route_id=route_id,
            status=request.status,
            progress=request.progress,
            actual_distance=request.actualDistance,
            actual_duration=request.actualDuration,
            actual_fuel=request.actualFuel,
            end_time=request.endTime
        )
        
        route = await handler.handle(command)
        
        return RouteResponse(
            id=str(route.id),
            _id=str(route.id),
            routeNumber=route.route_number,
            vendorId=route.vendor_id,
            vehicleId=route.vehicle_id,
            vehicleType=route.vehicle_type,
            driverName=route.driver_name,
            driverPhone=route.driver_phone,
            stops=[stop.to_dict() for stop in route.stops],
            status=route.status.value,
            startTime=route.start_time,
            endTime=route.end_time,
            estimatedDistance=route.estimated_distance,
            estimatedDuration=route.estimated_duration,
            estimatedFuel=route.estimated_fuel,
            actualDistance=route.actual_distance,
            actualDuration=route.actual_duration,
            actualFuel=route.actual_fuel,
            progress=route.progress,
            created_at=route.created_at,
            updated_at=route.updated_at,
            createdAt=route.created_at.isoformat() if route.created_at else None,
            updatedAt=route.updated_at.isoformat() if route.updated_at else None
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
    "/routes/{route_id}",
    response_model=dict,
    summary="Eliminar ruta",
    description="Elimina una ruta"
)
async def delete_route(
    route_id: str,
    handler=Depends(get_delete_route_handler)
):
    """Eliminar ruta"""
    try:
        command = DeleteRouteCommand(route_id=route_id)
        await handler.handle(command)
        
        return {"message": "Ruta eliminada exitosamente"}
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
    "/routes/generate-optimal",
    response_model=RouteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generar ruta óptima",
    description="Genera una ruta óptima basada en los IDs de órdenes proporcionados"
)
async def generate_optimal_route(
    request: GenerateOptimalRouteRequest,
    handler=Depends(get_generate_optimal_route_handler)
):
    """Generar ruta óptima"""
    try:
        command = GenerateOptimalRouteCommand(
            order_ids=request.orderIds,
            vehicle_type=request.vehicleType
        )
        
        route = await handler.handle(command)
        
        return RouteResponse(
            id=str(route.id),
            _id=str(route.id),
            routeNumber=route.route_number,
            vendorId=route.vendor_id,
            vehicleId=route.vehicle_id,
            vehicleType=route.vehicle_type,
            driverName=route.driver_name,
            driverPhone=route.driver_phone,
            stops=[stop.to_dict() for stop in route.stops],
            status=route.status.value,
            startTime=route.start_time,
            endTime=route.end_time,
            estimatedDistance=route.estimated_distance,
            estimatedDuration=route.estimated_duration,
            estimatedFuel=route.estimated_fuel,
            actualDistance=route.actual_distance,
            actualDuration=route.actual_duration,
            actualFuel=route.actual_fuel,
            progress=route.progress,
            created_at=route.created_at,
            updated_at=route.updated_at,
            createdAt=route.created_at.isoformat() if route.created_at else None,
            updatedAt=route.updated_at.isoformat() if route.updated_at else None
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

