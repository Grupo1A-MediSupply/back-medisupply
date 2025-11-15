"""
Rutas de la API de productos
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from ...application.commands import BatchData

from ...application.commands import (
    CreateProductCommand,
    UpdateProductCommand,
    AddStockCommand,
    RemoveStockCommand,
    DeactivateProductCommand,
    ActivateProductCommand,
    DeleteProductCommand
)
from ...application.queries import (
    GetProductByIdQuery,
    GetProductByNameQuery,
    GetAllProductsQuery,
    GetProductStockQuery
)
from ..dependencies import (
    get_create_product_handler,
    get_update_product_handler,
    get_add_stock_handler,
    get_remove_stock_handler,
    get_deactivate_product_handler,
    get_activate_product_handler,
    get_delete_product_handler,
    get_product_by_id_handler,
    get_product_by_name_handler,
    get_all_products_handler,
    get_product_stock_handler
)

router = APIRouter()


# ========== Schemas ==========

class BatchRequest(BaseModel):
    """Request para batch"""
    batch: str
    quantity: int
    expiry: Optional[datetime] = None
    location: Optional[str] = None


class CreateProductRequest(BaseModel):
    """Request para crear producto"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    price: float = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)
    expiry: Optional[datetime] = None
    lot: Optional[str] = None
    warehouse: Optional[str] = None
    supplier: Optional[str] = None
    category: Optional[str] = None
    batches: Optional[List[BatchRequest]] = None
    vendor_id: Optional[str] = None
    vendorId: Optional[str] = None  # Alias según especificación
    is_active: bool = True


class UpdateProductRequest(BaseModel):
    """Request para actualizar producto"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    expiry: Optional[datetime] = None
    lot: Optional[str] = None
    warehouse: Optional[str] = None
    supplier: Optional[str] = None
    category: Optional[str] = None
    batches: Optional[List[BatchRequest]] = None


class UpdateStockRequest(BaseModel):
    """Request para actualizar stock"""
    amount: int = Field(..., gt=0)


class ProductResponse(BaseModel):
    """Response de producto"""
    id: Optional[str] = None
    _id: Optional[str] = None  # Alias según especificación
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    expiry: Optional[datetime] = None
    lot: Optional[str] = None
    warehouse: Optional[str] = None
    supplier: Optional[str] = None
    category: Optional[str] = None
    batches: Optional[List[dict]] = None
    vendor_id: Optional[str] = None
    vendorId: Optional[str] = None  # Alias según especificación
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class MessageResponse(BaseModel):
    """Response de mensaje"""
    message: str


class StockResponse(BaseModel):
    """Response de stock"""
    product_id: str
    stock: int


# ========== Endpoints ==========

@router.post(
    "/products",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Crear producto",
    description="Crea un nuevo producto"
)
async def create_product(
    request: CreateProductRequest,
    handler=Depends(get_create_product_handler)
):
    """Crear nuevo producto"""
    try:
        # Convertir batches
        batches = None
        if request.batches:
            batches = [
                BatchData(
                    batch=b.batch,
                    quantity=b.quantity,
                    expiry=b.expiry,
                    location=b.location
                )
                for b in request.batches
            ]
        
        vendor_id = request.vendorId or request.vendor_id
        
        command = CreateProductCommand(
            name=request.name,
            description=request.description,
            price=request.price,
            stock=request.stock,
            expiry=request.expiry,
            lot=request.lot,
            warehouse=request.warehouse,
            supplier=request.supplier,
            category=request.category,
            batches=batches,
            vendor_id=vendor_id,
            is_active=request.is_active
        )
        
        product = await handler.handle(command)
        
        # Retornar según especificación (con wrapper "message" y "product")
        return {
            "message": "Producto creado exitosamente",
            "product": ProductResponse(
                id=str(product.id),
                _id=str(product.id),
                name=str(product.name),
                description=str(product.description) if product.description else None,
                price=product.price.amount,
                stock=product.stock.quantity,
                expiry=product.expiry,
                lot=str(product.lot) if product.lot else None,
                warehouse=str(product.warehouse) if product.warehouse else None,
                supplier=str(product.supplier) if product.supplier else None,
                category=str(product.category) if product.category else None,
                batches=[batch.to_dict() for batch in product.batches] if product.batches else None,
                vendor_id=str(product.vendor_id) if product.vendor_id else None,
                vendorId=str(product.vendor_id) if product.vendor_id else None,
                is_active=product.is_active,
                created_at=product.created_at,
                updated_at=product.updated_at
            ).dict(exclude_none=True)
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get(
    "/products",
    response_model=dict,
    summary="Listar productos",
    description="Lista todos los productos"
)
async def get_products(
    search: Optional[str] = None,
    category: Optional[str] = None,
    lowStock: Optional[bool] = None,
    active_only: bool = True,
    handler=Depends(get_all_products_handler)
):
    """Listar productos"""
    try:
        query = GetAllProductsQuery(
            active_only=active_only,
            search=search,
            category=category,
            low_stock_only=lowStock or False
        )
        
        products = await handler.handle(query)
        
        # Retornar según especificación (con wrapper "products")
        return {
            "products": [
                ProductResponse(
                    id=str(product.id),
                    _id=str(product.id),
                    name=str(product.name),
                    description=str(product.description) if product.description else None,
                    price=product.price.amount,
                    stock=product.stock.quantity,
                    expiry=product.expiry,
                    lot=str(product.lot) if product.lot else None,
                    warehouse=str(product.warehouse) if product.warehouse else None,
                    supplier=str(product.supplier) if product.supplier else None,
                    category=str(product.category) if product.category else None,
                    batches=[batch.to_dict() for batch in product.batches] if product.batches else None,
                    vendor_id=str(product.vendor_id) if product.vendor_id else None,
                    vendorId=str(product.vendor_id) if product.vendor_id else None,
                    is_active=product.is_active,
                    created_at=product.created_at,
                    updated_at=product.updated_at
                ).dict(exclude_none=True)
                for product in products
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get(
    "/products/{product_id}",
    response_model=dict,
    summary="Obtener producto",
    description="Obtiene un producto por su ID"
)
async def get_product(
    product_id: str,
    handler=Depends(get_product_by_id_handler)
):
    """Obtener producto por ID"""
    try:
        query = GetProductByIdQuery(product_id=product_id)
        
        product = await handler.handle(query)
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado"
            )
        
        # Retornar según especificación (con wrapper "product")
        return {
            "product": ProductResponse(
                id=str(product.id),
                _id=str(product.id),
                name=str(product.name),
                description=str(product.description) if product.description else None,
                price=product.price.amount,
                stock=product.stock.quantity,
                expiry=product.expiry,
                lot=str(product.lot) if product.lot else None,
                warehouse=str(product.warehouse) if product.warehouse else None,
                supplier=str(product.supplier) if product.supplier else None,
                category=str(product.category) if product.category else None,
                batches=[batch.to_dict() for batch in product.batches] if product.batches else None,
                vendor_id=str(product.vendor_id) if product.vendor_id else None,
                vendorId=str(product.vendor_id) if product.vendor_id else None,
                is_active=product.is_active,
                created_at=product.created_at,
                updated_at=product.updated_at
            ).dict(exclude_none=True)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.put(
    "/products/{product_id}",
    response_model=dict,
    summary="Actualizar producto",
    description="Actualiza un producto existente"
)
async def update_product(
    product_id: str,
    request: UpdateProductRequest,
    handler=Depends(get_update_product_handler)
):
    """Actualizar producto"""
    try:
        # Convertir batches
        batches = None
        if request.batches:
            batches = [
                BatchData(
                    batch=b.batch,
                    quantity=b.quantity,
                    expiry=b.expiry,
                    location=b.location
                )
                for b in request.batches
            ]
        
        command = UpdateProductCommand(
            product_id=product_id,
            name=request.name,
            description=request.description,
            price=request.price,
            expiry=request.expiry,
            lot=request.lot,
            warehouse=request.warehouse,
            supplier=request.supplier,
            category=request.category,
            batches=batches
        )
        
        product = await handler.handle(command)
        
        # Retornar según especificación (con wrapper "product" y "message")
        return {
            "message": "Producto actualizado exitosamente",
            "product": ProductResponse(
                id=str(product.id),
                _id=str(product.id),
                name=str(product.name),
                description=str(product.description) if product.description else None,
                price=product.price.amount,
                stock=product.stock.quantity,
                expiry=product.expiry,
                lot=str(product.lot) if product.lot else None,
                warehouse=str(product.warehouse) if product.warehouse else None,
                supplier=str(product.supplier) if product.supplier else None,
                category=str(product.category) if product.category else None,
                batches=[batch.to_dict() for batch in product.batches] if product.batches else None,
                vendor_id=str(product.vendor_id) if product.vendor_id else None,
                vendorId=str(product.vendor_id) if product.vendor_id else None,
                is_active=product.is_active,
                created_at=product.created_at,
                updated_at=product.updated_at
            ).dict(exclude_none=True)
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post(
    "/products/{product_id}/stock/add",
    response_model=StockResponse,
    summary="Agregar stock",
    description="Agrega stock a un producto"
)
async def add_stock(
    product_id: str,
    request: UpdateStockRequest,
    handler=Depends(get_add_stock_handler)
):
    """Agregar stock"""
    try:
        command = AddStockCommand(
            product_id=product_id,
            amount=request.amount
        )
        
        product = await handler.handle(command)
        
        return StockResponse(
            product_id=str(product.id),
            stock=product.stock.quantity
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post(
    "/products/{product_id}/stock/remove",
    response_model=StockResponse,
    summary="Remover stock",
    description="Remueve stock de un producto"
)
async def remove_stock(
    product_id: str,
    request: UpdateStockRequest,
    handler=Depends(get_remove_stock_handler)
):
    """Remover stock"""
    try:
        command = RemoveStockCommand(
            product_id=product_id,
            amount=request.amount
        )
        
        product = await handler.handle(command)
        
        return StockResponse(
            product_id=str(product.id),
            stock=product.stock.quantity
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post(
    "/products/{product_id}/deactivate",
    response_model=MessageResponse,
    summary="Desactivar producto",
    description="Desactiva un producto"
)
async def deactivate_product(
    product_id: str,
    handler=Depends(get_deactivate_product_handler)
):
    """Desactivar producto"""
    try:
        command = DeactivateProductCommand(product_id=product_id)
        
        await handler.handle(command)
        
        return MessageResponse(message="Producto desactivado exitosamente")
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post(
    "/products/{product_id}/activate",
    response_model=MessageResponse,
    summary="Activar producto",
    description="Activa un producto"
)
async def activate_product(
    product_id: str,
    handler=Depends(get_activate_product_handler)
):
    """Activar producto"""
    try:
        command = ActivateProductCommand(product_id=product_id)
        
        await handler.handle(command)
        
        return MessageResponse(message="Producto activado exitosamente")
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.delete(
    "/products/{product_id}",
    response_model=MessageResponse,
    summary="Eliminar producto",
    description="Elimina un producto"
)
async def delete_product(
    product_id: str,
    handler=Depends(get_delete_product_handler)
):
    """Eliminar producto"""
    try:
        command = DeleteProductCommand(product_id=product_id)
        
        deleted = await handler.handle(command)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado"
            )
        
        return MessageResponse(message="Producto eliminado exitosamente")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get(
    "/products/{product_id}/stock",
    response_model=StockResponse,
    summary="Obtener stock",
    description="Obtiene el stock de un producto"
)
async def get_product_stock(
    product_id: str,
    handler=Depends(get_product_stock_handler)
):
    """Obtener stock de producto"""
    try:
        query = GetProductStockQuery(product_id=product_id)
        
        stock = await handler.handle(query)
        
        if stock is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado"
            )
        
        return StockResponse(
            product_id=product_id,
            stock=stock
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post(
    "/products/bulk-upload",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Carga masiva de productos",
    description="Crea múltiples productos en una sola operación"
)
async def bulk_upload_products(
    products: List[CreateProductRequest],
    handler=Depends(get_create_product_handler)
):
    """Carga masiva de productos"""
    try:
        created_products = []
        
        for product_request in products:
            # Convertir batches
            batches = None
            if product_request.batches:
                batches = [
                    BatchData(
                        batch=b.batch,
                        quantity=b.quantity,
                        expiry=b.expiry,
                        location=b.location
                    )
                    for b in product_request.batches
                ]
            
            vendor_id = product_request.vendorId or product_request.vendor_id
            
            command = CreateProductCommand(
                name=product_request.name,
                description=product_request.description,
                price=product_request.price,
                stock=product_request.stock,
                expiry=product_request.expiry,
                lot=product_request.lot,
                warehouse=product_request.warehouse,
                supplier=product_request.supplier,
                category=product_request.category,
                batches=batches,
                vendor_id=vendor_id,
                is_active=product_request.is_active
            )
            
            product = await handler.handle(command)
            
            created_products.append(
                ProductResponse(
                    id=str(product.id),
                    _id=str(product.id),
                    name=str(product.name),
                    description=str(product.description) if product.description else None,
                    price=product.price.amount,
                    stock=product.stock.quantity,
                    expiry=product.expiry,
                    lot=str(product.lot) if product.lot else None,
                    warehouse=str(product.warehouse) if product.warehouse else None,
                    supplier=str(product.supplier) if product.supplier else None,
                    category=str(product.category) if product.category else None,
                    batches=[batch.to_dict() for batch in product.batches] if product.batches else None,
                    vendor_id=str(product.vendor_id) if product.vendor_id else None,
                    vendorId=str(product.vendor_id) if product.vendor_id else None,
                    is_active=product.is_active,
                    created_at=product.created_at,
                    updated_at=product.updated_at
                ).dict(exclude_none=True)
            )
        
        return {
            "message": "Productos cargados exitosamente",
            "products": created_products
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

