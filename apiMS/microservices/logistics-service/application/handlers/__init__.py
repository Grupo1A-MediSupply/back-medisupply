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
    CreateRouteCommand, AddStopCommand, RemoveStopCommand,
    StartRouteCommand, CompleteRouteCommand, CancelRouteCommand,
    UpdateTrackingCommand
)
from ..queries import (
    GetRouteByIdQuery, GetRoutesByVehicleQuery, GetRoutesByStatusQuery,
    GetTrackingInfoQuery, GetAllRoutesQuery
)
from ...domain.entities import Route, Stop, ETA, RouteStatus
from ...domain.events import (
    RouteCreatedEvent, RouteStartedEvent, RouteCompletedEvent, RouteCancelledEvent
)
from ...domain.ports import ILogisticsRepository


class CreateRouteCommandHandler:
    """Handler para el comando CreateRoute"""
    
    def __init__(self, logistics_repository: ILogisticsRepository):
        self.logistics_repository = logistics_repository
    
    async def handle(self, command: CreateRouteCommand) -> Route:
        """Manejar comando de creación de ruta"""
        # Convertir stops
        stops = []
        for stop_data in command.stops:
            stop_eta = None
            if stop_data.get("eta"):
                from datetime import datetime
                stop_eta = ETA(
                    date=stop_data["eta"]["date"],
                    window_minutes=stop_data["eta"]["windowMinutes"]
                )
            
            stop = Stop(
                order_id=stop_data["orderId"],
                priority=stop_data.get("priority", 1),
                eta=stop_eta
            )
            stops.append(stop)
        
        # Crear ruta
        route = Route.create(
            stops=stops,
            vehicle_id=command.vehicle_id
        )
        
        # Guardar ruta
        route = await self.logistics_repository.save(route)
        
        # Publicar eventos
        route._record_event(RouteCreatedEvent(
            route_id=str(route.id),
            vehicle_id=route.vehicle_id
        ))
        
        for event in route.get_domain_events():
            await event_bus.publish(event)
        
        route.clear_domain_events()
        
        return route


class StartRouteCommandHandler:
    """Handler para el comando StartRoute"""
    
    def __init__(self, logistics_repository: ILogisticsRepository):
        self.logistics_repository = logistics_repository
    
    async def handle(self, command: StartRouteCommand) -> Route:
        """Manejar comando de iniciar ruta"""
        route = await self.logistics_repository.find_by_id(EntityId(command.route_id))
        if not route:
            raise ValueError(f"Ruta {command.route_id} no encontrada")
        
        route.start_route(command.vehicle_id)
        
        # Publicar eventos
        route._record_event(RouteStartedEvent(
            route_id=str(route.id),
            vehicle_id=command.vehicle_id
        ))
        
        for event in route.get_domain_events():
            await event_bus.publish(event)
        
        route.clear_domain_events()
        
        route = await self.logistics_repository.save(route)
        
        return route


class CompleteRouteCommandHandler:
    """Handler para el comando CompleteRoute"""
    
    def __init__(self, logistics_repository: ILogisticsRepository):
        self.logistics_repository = logistics_repository
    
    async def handle(self, command: CompleteRouteCommand) -> Route:
        """Manejar comando de completar ruta"""
        route = await self.logistics_repository.find_by_id(EntityId(command.route_id))
        if not route:
            raise ValueError(f"Ruta {command.route_id} no encontrada")
        
        route.complete_route()
        
        # Publicar eventos
        route._record_event(RouteCompletedEvent(route_id=str(route.id)))
        
        for event in route.get_domain_events():
            await event_bus.publish(event)
        
        route.clear_domain_events()
        
        route = await self.logistics_repository.save(route)
        
        return route


class CancelRouteCommandHandler:
    """Handler para el comando CancelRoute"""
    
    def __init__(self, logistics_repository: ILogisticsRepository):
        self.logistics_repository = logistics_repository
    
    async def handle(self, command: CancelRouteCommand) -> Route:
        """Manejar comando de cancelar ruta"""
        route = await self.logistics_repository.find_by_id(EntityId(command.route_id))
        if not route:
            raise ValueError(f"Ruta {command.route_id} no encontrada")
        
        route.cancel_route()
        
        # Publicar eventos
        route._record_event(RouteCancelledEvent(route_id=str(route.id)))
        
        for event in route.get_domain_events():
            await event_bus.publish(event)
        
        route.clear_domain_events()
        
        route = await self.logistics_repository.save(route)
        
        return route


# Query Handlers

class GetRouteByIdQueryHandler:
    """Handler para la query GetRouteById"""
    
    def __init__(self, logistics_repository: ILogisticsRepository):
        self.logistics_repository = logistics_repository
    
    async def handle(self, query: GetRouteByIdQuery) -> Route:
        """Manejar query de obtener ruta por ID"""
        route = await self.logistics_repository.find_by_id(EntityId(query.route_id))
        if not route:
            raise ValueError(f"Ruta {query.route_id} no encontrada")
        
        return route


class GetRoutesByVehicleQueryHandler:
    """Handler para la query GetRoutesByVehicle"""
    
    def __init__(self, logistics_repository: ILogisticsRepository):
        self.logistics_repository = logistics_repository
    
    async def handle(self, query: GetRoutesByVehicleQuery) -> list:
        """Manejar query de obtener rutas por vehículo"""
        routes = await self.logistics_repository.find_by_vehicle_id(query.vehicle_id)
        return routes[query.skip:query.skip + query.limit]


class GetRoutesByStatusQueryHandler:
    """Handler para la query GetRoutesByStatus"""
    
    def __init__(self, logistics_repository: ILogisticsRepository):
        self.logistics_repository = logistics_repository
    
    async def handle(self, query: GetRoutesByStatusQuery) -> list:
        """Manejar query de obtener rutas por estado"""
        status_enum = RouteStatus(query.status)
        routes = await self.logistics_repository.find_by_status(status_enum)
        return routes[query.skip:query.skip + query.limit]


class GetAllRoutesQueryHandler:
    """Handler para la query GetAllRoutes"""
    
    def __init__(self, logistics_repository: ILogisticsRepository):
        self.logistics_repository = logistics_repository
    
    async def handle(self, query: GetAllRoutesQuery) -> list:
        """Manejar query de obtener todas las rutas"""
        routes = await self.logistics_repository.find_all(skip=query.skip, limit=query.limit)
        return routes

