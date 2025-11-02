# Infrastructure Adapters

Adaptadores para comunicación con servicios externos.

## ProductServiceAdapter

Adaptador para comunicarse con el Product Service y validar productos antes de crear órdenes.

### Métodos

#### validate_products(sku_ids: list) -> bool

Valida que todos los productos especificados existen y están activos.

```python
adapter = ProductServiceAdapter()
await adapter.validate_products(['SKU001', 'SKU002'])
# Si todos son válidos → True
# Si alguno no existe → ValueError
```

#### get_product_info(product_id: str) -> dict

Obtiene información detallada de un producto.

```python
adapter = ProductServiceAdapter()
product = await adapter.get_product_info('SKU001')
# Retorna: {'id': 'SKU001', 'name': 'Producto', 'price': 10.0, ...}
```

## Uso en Handlers

```python
class CreateOrderCommandHandler:
    def __init__(self, order_repository, product_adapter):
        self.order_repository = order_repository
        self.product_adapter = product_adapter
    
    async def handle(self, command):
        # Validar productos
        await self.product_adapter.validate_products(
            [item["skuId"] for item in command.items]
        )
        
        # Crear orden si validación es exitosa
        order = Order.create(items=order_items)
        return await self.order_repository.save(order)
```

## Configuración

La URL del Product Service se configura mediante variable de entorno:

```bash
PRODUCT_SERVICE_URL=http://product-service:8002
```

En producción:
```bash
PRODUCT_SERVICE_URL=http://product-service.internal:8002
```

