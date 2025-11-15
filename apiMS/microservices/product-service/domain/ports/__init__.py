"""
Puertos (interfaces) del dominio de productos
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
from ..value_objects import ProductName
from ..entities import Product


class IProductRepository(ABC):
    """Puerto (interfaz) para el repositorio de productos"""
    
    @abstractmethod
    async def save(self, product: Product) -> Product:
        """Guardar producto"""
        pass
    
    @abstractmethod
    async def find_by_id(self, product_id: EntityId) -> Optional[Product]:
        """Buscar producto por ID"""
        pass
    
    @abstractmethod
    async def find_by_name(self, name: ProductName) -> Optional[Product]:
        """Buscar producto por nombre"""
        pass
    
    @abstractmethod
    async def find_all(self, active_only: bool = True) -> List[Product]:
        """Listar todos los productos"""
        pass
    
    @abstractmethod
    async def delete(self, product_id: EntityId) -> bool:
        """Eliminar producto"""
        pass
    
    @abstractmethod
    async def exists_by_id(self, product_id: EntityId) -> bool:
        """Verificar si existe un producto con ese ID"""
        pass

