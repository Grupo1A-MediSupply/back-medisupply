"""
Repositorios de infraestructura para logística
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, DateTime, Integer, Float, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
import sys
from pathlib import Path
from json import dumps, loads

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from shared.domain.value_objects import EntityId
from ...domain.entities import Route, Stop, ETA, RouteStatus
from ...domain.ports import ILogisticsRepository

Base = declarative_base()


class RouteModel(Base):
    """Modelo de base de datos para Route"""
    __tablename__ = "routes"
    
    id = Column(String, primary_key=True)
    route_number = Column(String, unique=True, index=True)
    vendor_id = Column(String, nullable=True, index=True)
    vehicle_id = Column(String, nullable=True, index=True)
    vehicle_type = Column(String, nullable=True)
    driver_name = Column(String, nullable=True)
    driver_phone = Column(String, nullable=True)
    status = Column(SQLEnum(RouteStatus), nullable=False, default=RouteStatus.PLANNED, index=True)
    stops_json = Column(Text, nullable=False)  # JSON serializado de stops
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    estimated_distance = Column(Float, nullable=True)
    estimated_duration = Column(Integer, nullable=True)  # en minutos
    estimated_fuel = Column(Float, nullable=True)
    actual_distance = Column(Float, nullable=True)
    actual_duration = Column(Integer, nullable=True)  # en minutos
    actual_fuel = Column(Float, nullable=True)
    progress = Column(Float, default=0.0)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)


class SQLAlchemyLogisticsRepository(ILogisticsRepository):
    """Repositorio de logística con SQLAlchemy"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def save(self, route: Route) -> Route:
        """Guardar ruta"""
        # Buscar si existe
        existing = self.db.query(RouteModel).filter(
            RouteModel.id == str(route.id)
        ).first()
        
        if existing:
            # Actualizar
            existing.route_number = route.route_number
            existing.vendor_id = route.vendor_id
            existing.vehicle_id = route.vehicle_id
            existing.vehicle_type = route.vehicle_type
            existing.driver_name = route.driver_name
            existing.driver_phone = route.driver_phone
            existing.status = route.status
            existing.stops_json = dumps([stop.to_dict() for stop in route.stops])
            existing.start_time = route.start_time
            existing.end_time = route.end_time
            existing.estimated_distance = route.estimated_distance
            existing.estimated_duration = route.estimated_duration
            existing.estimated_fuel = route.estimated_fuel
            existing.actual_distance = route.actual_distance
            existing.actual_duration = route.actual_duration
            existing.actual_fuel = route.actual_fuel
            existing.progress = route.progress
            existing.updated_at = route.updated_at
        else:
            # Crear nuevo
            model = RouteModel(
                id=str(route.id),
                route_number=route.route_number,
                vendor_id=route.vendor_id,
                vehicle_id=route.vehicle_id,
                vehicle_type=route.vehicle_type,
                driver_name=route.driver_name,
                driver_phone=route.driver_phone,
                status=route.status,
                stops_json=dumps([stop.to_dict() for stop in route.stops]),
                start_time=route.start_time,
                end_time=route.end_time,
                estimated_distance=route.estimated_distance,
                estimated_duration=route.estimated_duration,
                estimated_fuel=route.estimated_fuel,
                actual_distance=route.actual_distance,
                actual_duration=route.actual_duration,
                actual_fuel=route.actual_fuel,
                progress=route.progress,
                created_at=route.created_at,
                updated_at=route.updated_at
            )
            self.db.add(model)
        
        self.db.commit()
        
        return route
    
    def _to_domain(self, model: RouteModel) -> Route:
        """Convertir modelo de DB a entidad de dominio"""
        stops_data = loads(model.stops_json)
        stops = []
        
        for stop_data in stops_data:
            from datetime import datetime
            eta = None
            if stop_data.get("eta"):
                eta = ETA(
                    date=datetime.fromisoformat(stop_data["eta"]["date"]),
                    window_minutes=stop_data["eta"]["windowMinutes"]
                )
            
            stop = Stop(
                order_id=stop_data["orderId"],
                priority=stop_data["priority"],
                eta=eta
            )
            stops.append(stop)
        
        return Route(
            route_id=EntityId(model.id),
            stops=stops,
            vehicle_id=model.vehicle_id,
            status=model.status,
            route_number=model.route_number,
            vendor_id=model.vendor_id,
            vehicle_type=model.vehicle_type,
            driver_name=model.driver_name,
            driver_phone=model.driver_phone,
            start_time=model.start_time,
            end_time=model.end_time,
            estimated_distance=model.estimated_distance,
            estimated_duration=model.estimated_duration,
            estimated_fuel=model.estimated_fuel,
            actual_distance=model.actual_distance,
            actual_duration=model.actual_duration,
            actual_fuel=model.actual_fuel,
            progress=model.progress
        )
    
    async def find_by_id(self, route_id: EntityId) -> Optional[Route]:
        """Buscar ruta por ID"""
        model = self.db.query(RouteModel).filter(
            RouteModel.id == str(route_id)
        ).first()
        
        return self._to_domain(model) if model else None
    
    async def find_by_vehicle_id(self, vehicle_id: str) -> List[Route]:
        """Buscar rutas por vehículo"""
        models = self.db.query(RouteModel).filter(
            RouteModel.vehicle_id == vehicle_id
        ).all()
        
        return [self._to_domain(model) for model in models]
    
    async def find_by_status(self, status: RouteStatus) -> List[Route]:
        """Buscar rutas por estado"""
        models = self.db.query(RouteModel).filter(
            RouteModel.status == status
        ).all()
        
        return [self._to_domain(model) for model in models]
    
    async def find_all(self, skip: int = 0, limit: int = 100, status: Optional[RouteStatus] = None) -> List[Route]:
        """Listar todas las rutas"""
        query = self.db.query(RouteModel)
        
        if status:
            query = query.filter(RouteModel.status == status)
        
        models = query.offset(skip).limit(limit).all()
        
        return [self._to_domain(model) for model in models]
    
    async def delete(self, route_id: EntityId) -> bool:
        """Eliminar ruta"""
        model = self.db.query(RouteModel).filter(
            RouteModel.id == str(route_id)
        ).first()
        
        if model:
            self.db.delete(model)
            self.db.commit()
            return True
        
        return False
    
    async def exists_by_id(self, route_id: EntityId) -> bool:
        """Verificar si existe ruta con ese ID"""
        count = self.db.query(RouteModel).filter(
            RouteModel.id == str(route_id)
        ).count()
        
        return count > 0

