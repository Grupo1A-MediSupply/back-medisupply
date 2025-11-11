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
    vehicle_id = Column(String, nullable=True)
    status = Column(SQLEnum(RouteStatus), nullable=False, default=RouteStatus.PLANNED)
    stops_json = Column(Text, nullable=False)  # JSON serializado de stops
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
            existing.vehicle_id = route.vehicle_id
            existing.status = route.status
            existing.stops_json = dumps([stop.to_dict() for stop in route.stops])
            existing.updated_at = route.updated_at
        else:
            # Crear nuevo
            model = RouteModel(
                id=str(route.id),
                vehicle_id=route.vehicle_id,
                status=route.status,
                stops_json=dumps([stop.to_dict() for stop in route.stops]),
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
            status=model.status
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
    
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[Route]:
        """Listar todas las rutas"""
        models = self.db.query(RouteModel).offset(skip).limit(limit).all()
        
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

