"""
Handlers para comandos y queries del servicio de productos
"""
from typing import Optional, List
from uuid import uuid4
from datetime import datetime
import sys
from pathlib import Path

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from shared.domain.value_objects import EntityId, Money
from shared.domain.events import event_bus
from ..commands import (
    CreateProductCommand,
    UpdateProductCommand,
    AddStockCommand,
    RemoveStockCommand,
    DeactivateProductCommand,
    ActivateProductCommand,
    DeleteProductCommand
)
from ..queries import (
    GetProductByIdQuery,
    GetProductByNameQuery,
    GetAllProductsQuery,
    GetProductStockQuery
)
from ...domain.entities import Product, Batch
from ...domain.value_objects import (
    ProductName, ProductDescription, Stock, Lot, Warehouse, 
    Supplier, Category, VendorId
)
from ...domain.ports import IProductRepository


# ========== Command Handlers ==========

class CreateProductCommandHandler:
    """Handler para el comando CreateProduct"""
    
    def __init__(self, product_repository: IProductRepository):
        self.product_repository = product_repository
    
    async def handle(self, command: CreateProductCommand) -> Product:
        """Manejar comando de creación de producto"""
        # Convertir batches
        batches = None
        if command.batches:
            batches = [
                Batch(
                    batch=b.batch,
                    quantity=b.quantity,
                    expiry=b.expiry,
                    location=b.location
                )
                for b in command.batches
            ]
        
        # Crear producto
        product = Product.create(
            product_id=EntityId(str(uuid4())),
            name=ProductName(command.name),
            price=Money(command.price),
            description=ProductDescription(command.description) if command.description else None,
            stock=Stock(command.stock),
            expiry=command.expiry,
            lot=Lot(command.lot) if command.lot else None,
            warehouse=Warehouse(command.warehouse) if command.warehouse else None,
            supplier=Supplier(command.supplier) if command.supplier else None,
            category=Category(command.category) if command.category else None,
            batches=batches,
            vendor_id=VendorId(command.vendor_id) if command.vendor_id else None,
            is_active=command.is_active
        )
        
        # Guardar producto
        product = await self.product_repository.save(product)
        
        # Publicar eventos de dominio
        for event in product.get_domain_events():
            await event_bus.publish(event)
        
        product.clear_domain_events()
        
        return product


class UpdateProductCommandHandler:
    """Handler para el comando UpdateProduct"""
    
    def __init__(self, product_repository: IProductRepository):
        self.product_repository = product_repository
    
    async def handle(self, command: UpdateProductCommand) -> Product:
        """Manejar comando de actualización de producto"""
        # Buscar producto
        product = await self.product_repository.find_by_id(EntityId(command.product_id))
        if not product:
            raise ValueError("Producto no encontrado")
        
        # Actualizar campos
        if command.name:
            product.update_name(ProductName(command.name))
        
        if command.description:
            product.update_description(ProductDescription(command.description))
        
        if command.price:
            product.update_price(Money(command.price))
        
        # Actualizar nuevos campos (necesitamos métodos en la entidad o actualizar directamente)
        # Por ahora, recreamos el producto con los nuevos valores
        if command.expiry is not None or command.lot or command.warehouse or command.supplier or command.category or command.batches:
            # Convertir batches
            batches = None
            if command.batches:
                batches = [
                    Batch(
                        batch=b.batch,
                        quantity=b.quantity,
                        expiry=b.expiry,
                        location=b.location
                    )
                    for b in command.batches
                ]
            
            # Actualizar campos directamente (esto requiere métodos setter o recrear)
            # Por simplicidad, actualizamos los campos directamente
            if command.expiry is not None:
                product._expiry = command.expiry
            if command.lot:
                product._lot = Lot(command.lot)
            if command.warehouse:
                product._warehouse = Warehouse(command.warehouse)
            if command.supplier:
                product._supplier = Supplier(command.supplier)
            if command.category:
                product._category = Category(command.category)
            if batches is not None:
                product._batches = batches
            product._updated_at = datetime.utcnow()
        
        # Guardar producto
        product = await self.product_repository.save(product)
        
        # Publicar eventos
        for event in product.get_domain_events():
            await event_bus.publish(event)
        
        product.clear_domain_events()
        
        return product


class AddStockCommandHandler:
    """Handler para el comando AddStock"""
    
    def __init__(self, product_repository: IProductRepository):
        self.product_repository = product_repository
    
    async def handle(self, command: AddStockCommand) -> Product:
        """Manejar comando de agregar stock"""
        # Buscar producto
        product = await self.product_repository.find_by_id(EntityId(command.product_id))
        if not product:
            raise ValueError("Producto no encontrado")
        
        # Agregar stock
        product.add_stock(command.amount)
        
        # Guardar producto
        product = await self.product_repository.save(product)
        
        # Publicar eventos
        for event in product.get_domain_events():
            await event_bus.publish(event)
        
        product.clear_domain_events()
        
        return product


class RemoveStockCommandHandler:
    """Handler para el comando RemoveStock"""
    
    def __init__(self, product_repository: IProductRepository):
        self.product_repository = product_repository
    
    async def handle(self, command: RemoveStockCommand) -> Product:
        """Manejar comando de remover stock"""
        # Buscar producto
        product = await self.product_repository.find_by_id(EntityId(command.product_id))
        if not product:
            raise ValueError("Producto no encontrado")
        
        # Remover stock
        product.remove_stock(command.amount)
        
        # Guardar producto
        product = await self.product_repository.save(product)
        
        # Publicar eventos
        for event in product.get_domain_events():
            await event_bus.publish(event)
        
        product.clear_domain_events()
        
        return product


class DeactivateProductCommandHandler:
    """Handler para el comando DeactivateProduct"""
    
    def __init__(self, product_repository: IProductRepository):
        self.product_repository = product_repository
    
    async def handle(self, command: DeactivateProductCommand) -> Product:
        """Manejar comando de desactivación de producto"""
        # Buscar producto
        product = await self.product_repository.find_by_id(EntityId(command.product_id))
        if not product:
            raise ValueError("Producto no encontrado")
        
        # Desactivar producto
        product.deactivate()
        
        # Guardar producto
        product = await self.product_repository.save(product)
        
        # Publicar eventos
        for event in product.get_domain_events():
            await event_bus.publish(event)
        
        product.clear_domain_events()
        
        return product


class ActivateProductCommandHandler:
    """Handler para el comando ActivateProduct"""
    
    def __init__(self, product_repository: IProductRepository):
        self.product_repository = product_repository
    
    async def handle(self, command: ActivateProductCommand) -> Product:
        """Manejar comando de activación de producto"""
        # Buscar producto
        product = await self.product_repository.find_by_id(EntityId(command.product_id))
        if not product:
            raise ValueError("Producto no encontrado")
        
        # Activar producto
        product.activate()
        
        # Guardar producto
        product = await self.product_repository.save(product)
        
        return product


class DeleteProductCommandHandler:
    """Handler para el comando DeleteProduct"""
    
    def __init__(self, product_repository: IProductRepository):
        self.product_repository = product_repository
    
    async def handle(self, command: DeleteProductCommand) -> bool:
        """Manejar comando de eliminación de producto"""
        return await self.product_repository.delete(EntityId(command.product_id))


# ========== Query Handlers ==========

class GetProductByIdQueryHandler:
    """Handler para la query GetProductById"""
    
    def __init__(self, product_repository: IProductRepository):
        self.product_repository = product_repository
    
    async def handle(self, query: GetProductByIdQuery) -> Optional[Product]:
        """Manejar query de obtener producto por ID"""
        return await self.product_repository.find_by_id(EntityId(query.product_id))


class GetProductByNameQueryHandler:
    """Handler para la query GetProductByName"""
    
    def __init__(self, product_repository: IProductRepository):
        self.product_repository = product_repository
    
    async def handle(self, query: GetProductByNameQuery) -> Optional[Product]:
        """Manejar query de obtener producto por nombre"""
        return await self.product_repository.find_by_name(ProductName(query.name))


class GetAllProductsQueryHandler:
    """Handler para la query GetAllProducts"""
    
    def __init__(self, product_repository: IProductRepository):
        self.product_repository = product_repository
    
    async def handle(self, query: GetAllProductsQuery) -> List[Product]:
        """Manejar query de obtener todos los productos"""
        return await self.product_repository.find_all(
            active_only=query.active_only,
            search=query.search,
            category=query.category,
            low_stock_only=query.low_stock_only
        )


class GetProductStockQueryHandler:
    """Handler para la query GetProductStock"""
    
    def __init__(self, product_repository: IProductRepository):
        self.product_repository = product_repository
    
    async def handle(self, query: GetProductStockQuery) -> Optional[int]:
        """Manejar query de obtener stock de producto"""
        product = await self.product_repository.find_by_id(EntityId(query.product_id))
        if not product:
            return None
        return product.stock.quantity

