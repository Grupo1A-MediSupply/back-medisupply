"""
Rutas de la API de productos
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

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

class CreateProductRequest(BaseModel):
    """Request para crear producto"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    price: float = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)
    is_active: bool = True


class UpdateProductRequest(BaseModel):
    """Request para actualizar producto"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[float] = Field(None, gt=0)


class UpdateStockRequest(BaseModel):
    """Request para actualizar stock"""
    amount: int = Field(..., gt=0)


class ProductResponse(BaseModel):
    """Response de producto"""
    id: str
    name: str
    description: Optional[str]
    price: float
    stock: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


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
    response_model=ProductResponse,
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
        command = CreateProductCommand(
            name=request.name,
            description=request.description,
            price=request.price,
            stock=request.stock,
            is_active=request.is_active
        )
        
        product = await handler.handle(command)
        
        return ProductResponse(
            id=str(product.id),
            name=str(product.name),
            description=str(product.description) if product.description else None,
            price=product.price.amount,
            stock=product.stock.quantity,
            is_active=product.is_active,
            created_at=product.created_at,
            updated_at=product.updated_at
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


@router.get(
    "/products",
    response_model=List[ProductResponse],
    summary="Listar productos",
    description="Lista todos los productos"
)
async def get_products(
    active_only: bool = True,
    handler=Depends(get_all_products_handler)
):
    """Listar productos"""
    try:
        query = GetAllProductsQuery(active_only=active_only)
        
        products = await handler.handle(query)
        
        return [
            ProductResponse(
                id=str(product.id),
                name=str(product.name),
                description=str(product.description) if product.description else None,
                price=product.price.amount,
                stock=product.stock.quantity,
                is_active=product.is_active,
                created_at=product.created_at,
                updated_at=product.updated_at
            )
            for product in products
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get(
    "/products/{product_id}",
    response_model=ProductResponse,
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
        
        return ProductResponse(
            id=str(product.id),
            name=str(product.name),
            description=str(product.description) if product.description else None,
            price=product.price.amount,
            stock=product.stock.quantity,
            is_active=product.is_active,
            created_at=product.created_at,
            updated_at=product.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.put(
    "/products/{product_id}",
    response_model=ProductResponse,
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
        command = UpdateProductCommand(
            product_id=product_id,
            name=request.name,
            description=request.description,
            price=request.price
        )
        
        product = await handler.handle(command)
        
        return ProductResponse(
            id=str(product.id),
            name=str(product.name),
            description=str(product.description) if product.description else None,
            price=product.price.amount,
            stock=product.stock.quantity,
            is_active=product.is_active,
            created_at=product.created_at,
            updated_at=product.updated_at
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

