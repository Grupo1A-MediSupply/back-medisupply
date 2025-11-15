"""
Cliente HTTP compartido para comunicación entre microservicios
"""
import httpx
from typing import Optional, Dict, Any
from datetime import timedelta


class HTTPClient:
    """Cliente HTTP para comunicación entre microservicios"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            follow_redirects=True
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self._client:
            await self._client.aclose()
    
    async def get(self, endpoint: str, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """GET request"""
        if not self._client:
            raise RuntimeError("HTTPClient debe usarse como context manager")
        
        response = await self._client.get(
            endpoint,
            params=params,
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    
    async def post(self, endpoint: str, json: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """POST request"""
        if not self._client:
            raise RuntimeError("HTTPClient debe usarse como context manager")
        
        response = await self._client.post(
            endpoint,
            json=json,
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    
    async def put(self, endpoint: str, json: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """PUT request"""
        if not self._client:
            raise RuntimeError("HTTPClient debe usarse como context manager")
        
        response = await self._client.put(
            endpoint,
            json=json,
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    
    async def delete(self, endpoint: str, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """DELETE request"""
        if not self._client:
            raise RuntimeError("HTTPClient debe usarse como context manager")
        
        response = await self._client.delete(endpoint, headers=headers)
        response.raise_for_status()
        return response.json() if response.content else {}


class AuthServiceClient:
    """Cliente para el servicio de autenticación"""
    
    def __init__(self, auth_service_url: str):
        self.client = HTTPClient(auth_service_url)
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verificar token JWT"""
        async with self.client:
            response = await self.client.get(
                "/api/v1/auth/verify",
                headers={"Authorization": f"Bearer {token}"}
            )
            return response
    
    async def get_current_user(self, token: str) -> Dict[str, Any]:
        """Obtener usuario actual"""
        async with self.client:
            response = await self.client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            return response


class ProductServiceClient:
    """Cliente para el servicio de productos"""
    
    def __init__(self, product_service_url: str):
        self.client = HTTPClient(product_service_url)
    
    async def get_product(self, product_id: str) -> Dict[str, Any]:
        """Obtener producto por ID"""
        async with self.client:
            response = await self.client.get(f"/api/v1/products/{product_id}")
            return response
    
    async def get_products(self, active_only: bool = True) -> list:
        """Listar productos"""
        async with self.client:
            response = await self.client.get(
                "/api/v1/products",
                params={"active_only": active_only}
            )
            return response
    
    async def update_stock(self, product_id: str, quantity: int, operation: str) -> Dict[str, Any]:
        """Actualizar stock de producto (operation: 'add' o 'remove')"""
        async with self.client:
            response = await self.client.post(
                f"/api/v1/products/{product_id}/stock/{operation}",
                json={"quantity": quantity}
            )
            return response


class OrderServiceClient:
    """Cliente para el servicio de órdenes"""
    
    def __init__(self, order_service_url: str):
        self.client = HTTPClient(order_service_url)
    
    async def get_order(self, order_id: str) -> Dict[str, Any]:
        """Obtener orden por ID"""
        async with self.client:
            response = await self.client.get(f"/api/v1/orders/{order_id}")
            return response
    
    async def update_order_status(self, order_id: str, status: str) -> Dict[str, Any]:
        """Actualizar estado de orden"""
        async with self.client:
            # Mapear el estado al endpoint correcto
            endpoint_map = {
                "CONFIRMED": f"/api/v1/orders/{order_id}/confirm",
                "CANCELLED": f"/api/v1/orders/{order_id}/cancel",
            }
            
            if status in endpoint_map:
                response = await self.client.post(endpoint_map[status])
                return response
            else:
                raise ValueError(f"Estado {status} no soportado")


class LogisticsServiceClient:
    """Cliente para el servicio de logística"""
    
    def __init__(self, logistics_service_url: str):
        self.client = HTTPClient(logistics_service_url)
    
    async def create_route(self, stops: list, vehicle_id: str = None) -> Dict[str, Any]:
        """Crear ruta"""
        async with self.client:
            response = await self.client.post(
                "/api/v1/routes",
                json={"stops": stops, "vehicleId": vehicle_id}
            )
            return response
    
    async def get_route(self, route_id: str) -> Dict[str, Any]:
        """Obtener ruta por ID"""
        async with self.client:
            response = await self.client.get(f"/api/v1/routes/{route_id}")
            return response
    
    async def start_route(self, route_id: str, vehicle_id: str) -> Dict[str, Any]:
        """Iniciar ruta"""
        async with self.client:
            response = await self.client.post(
                f"/api/v1/routes/{route_id}/start",
                json={"vehicleId": vehicle_id}
            )
            return response

