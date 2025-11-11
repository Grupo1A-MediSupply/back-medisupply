"""
Puertos (interfaces) del dominio de logística
"""
from abc import ABC, abstractmethod
from typing import Optional, List
import sys
from pathlib import Path

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from shared.domain.value_objects import EntityId
from ..entities import Route, RouteStatus


class ILogisticsRepository(ABC):
    """Puerto (interfaz) para el repositorio de logística"""
    
    @abstractmethod
    async def save(self, route: Route) -> Route:
        """Guardar ruta"""
        pass
    
    @abstractmethod
    async def find_by_id(self, route_id: EntityId) -> Optional[Route]:
        """Buscar ruta por ID"""
        pass
    
    @abstractmethod
    async def find_by_vehicle_id(self, vehicle_id: str) -> List[Route]:
        """Buscar rutas por vehículo"""
        pass
    
    @abstractmethod
    async def find_by_status(self, status: RouteStatus) -> List[Route]:
        """Buscar rutas por estado"""
        pass
    
    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[Route]:
        """Listar todas las rutas"""
        pass
    
    @abstractmethod
    async def delete(self, route_id: EntityId) -> bool:
        """Eliminar ruta"""
        pass
    
    @abstractmethod
    async def exists_by_id(self, route_id: EntityId) -> bool:
        """Verificar si existe una ruta con ese ID"""
        pass

