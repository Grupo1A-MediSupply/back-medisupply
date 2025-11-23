"""
Adaptador para comunicarse con el Product Service
"""
import sys
from pathlib import Path

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from shared.infrastructure.http_client import ProductServiceClient
from ...infrastructure.config import get_settings


class ProductServiceAdapter:
    """Adaptador para comunicación con el servicio de productos"""
    
    def __init__(self):
        self.settings = get_settings()
        product_service_url = self.settings.product_service_url
        self.client = ProductServiceClient(product_service_url)
    
    async def validate_products(self, sku_ids: list) -> bool:
        """
        Validar que todos los productos existen y están activos
        
        Returns:
            bool: True si todos los productos son válidos
        
        Raises:
            ValueError: Si algún producto no existe o no está activo
        """
        try:
            # Obtener todos los productos activos
            products = await self.client.get_products(active_only=True)
            
            # Crear un set de IDs de productos disponibles
            available_ids = {str(product['id']) for product in products}
            
            # Verificar que todos los SKUs estén disponibles
            for sku_id in sku_ids:
                if sku_id not in available_ids:
                    raise ValueError(f"Producto con SKU {sku_id} no encontrado o no está activo")
            
            return True
            
        except Exception as e:
            raise ValueError(f"Error al validar productos: {str(e)}")
    
    async def get_product_info(self, product_id: str) -> dict:
        """Obtener información de un producto"""
        try:
            product = await self.client.get_product(product_id)
            return product
        except Exception as e:
            raise ValueError(f"Error al obtener producto {product_id}: {str(e)}")

