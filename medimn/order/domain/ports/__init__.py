"""
Puertos (interfaces) del dominio de órdenes
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
from ..entities import Order, OrderStatus


class IOrderRepository(ABC):
    """Puerto (interfaz) para el repositorio de órdenes"""
    
    @abstractmethod
    async def save(self, order: Order) -> Order:
        """Guardar orden"""
        pass
    
    @abstractmethod
    async def find_by_id(self, order_id: EntityId) -> Optional[Order]:
        """Buscar orden por ID"""
        pass
    
    @abstractmethod
    async def find_by_status(self, status: OrderStatus) -> List[Order]:
        """Buscar órdenes por estado"""
        pass
    
    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[Order]:
        """Listar todas las órdenes"""
        pass
    
    @abstractmethod
    async def delete(self, order_id: EntityId) -> bool:
        """Eliminar orden"""
        pass
    
    @abstractmethod
    async def exists_by_id(self, order_id: EntityId) -> bool:
        """Verificar si existe una orden con ese ID"""
        pass

