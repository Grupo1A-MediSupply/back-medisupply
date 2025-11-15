# Shared Infrastructure

Infraestructura compartida entre todos los microservicios.

## Contenido

### http_client.py

Cliente HTTP base para comunicación entre microservicios usando `httpx`.

#### Clientes Disponibles

- **HTTPClient**: Cliente base con context manager
- **AuthServiceClient**: Cliente para servicio de autenticación
- **ProductServiceClient**: Cliente para servicio de productos
- **OrderServiceClient**: Cliente para servicio de órdenes
- **LogisticsServiceClient**: Cliente para servicio de logística

#### Ejemplo de Uso

```python
from shared.infrastructure.http_client import ProductServiceClient

# Crear cliente
client = ProductServiceClient("http://product-service:8002")

# Obtener producto
product = await client.get_product("SKU001")

# Listar productos
products = await client.get_products(active_only=True)

# Actualizar stock
await client.update_stock("SKU001", quantity=5, operation="add")
```

## Tests

Para testear servicios que usan clientes HTTP, mockear el cliente:

```python
from unittest.mock import AsyncMock

mock_client = AsyncMock()
mock_client.get_product.return_value = {
    "id": "SKU001",
    "name": "Producto Test",
    "price": 10.0
}
```

