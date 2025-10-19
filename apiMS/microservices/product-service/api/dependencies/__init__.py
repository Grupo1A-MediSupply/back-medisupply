"""
Dependencias de FastAPI para el servicio de productos
"""
from sqlalchemy.orm import Session
from fastapi import Depends

from ...infrastructure.database import get_db
from ...infrastructure.repositories import SQLAlchemyProductRepository
from ...application.handlers import (
    CreateProductCommandHandler,
    UpdateProductCommandHandler,
    AddStockCommandHandler,
    RemoveStockCommandHandler,
    DeactivateProductCommandHandler,
    ActivateProductCommandHandler,
    DeleteProductCommandHandler,
    GetProductByIdQueryHandler,
    GetProductByNameQueryHandler,
    GetAllProductsQueryHandler,
    GetProductStockQueryHandler
)


# Repositorios
def get_product_repository(db: Session = Depends(get_db)) -> SQLAlchemyProductRepository:
    """Obtener repositorio de productos"""
    return SQLAlchemyProductRepository(db)


# Command Handlers
def get_create_product_handler(
    product_repository: SQLAlchemyProductRepository = Depends(get_product_repository)
) -> CreateProductCommandHandler:
    """Obtener handler de creación de producto"""
    return CreateProductCommandHandler(product_repository)


def get_update_product_handler(
    product_repository: SQLAlchemyProductRepository = Depends(get_product_repository)
) -> UpdateProductCommandHandler:
    """Obtener handler de actualización de producto"""
    return UpdateProductCommandHandler(product_repository)


def get_add_stock_handler(
    product_repository: SQLAlchemyProductRepository = Depends(get_product_repository)
) -> AddStockCommandHandler:
    """Obtener handler de agregar stock"""
    return AddStockCommandHandler(product_repository)


def get_remove_stock_handler(
    product_repository: SQLAlchemyProductRepository = Depends(get_product_repository)
) -> RemoveStockCommandHandler:
    """Obtener handler de remover stock"""
    return RemoveStockCommandHandler(product_repository)


def get_deactivate_product_handler(
    product_repository: SQLAlchemyProductRepository = Depends(get_product_repository)
) -> DeactivateProductCommandHandler:
    """Obtener handler de desactivación de producto"""
    return DeactivateProductCommandHandler(product_repository)


def get_activate_product_handler(
    product_repository: SQLAlchemyProductRepository = Depends(get_product_repository)
) -> ActivateProductCommandHandler:
    """Obtener handler de activación de producto"""
    return ActivateProductCommandHandler(product_repository)


def get_delete_product_handler(
    product_repository: SQLAlchemyProductRepository = Depends(get_product_repository)
) -> DeleteProductCommandHandler:
    """Obtener handler de eliminación de producto"""
    return DeleteProductCommandHandler(product_repository)


# Query Handlers
def get_product_by_id_handler(
    product_repository: SQLAlchemyProductRepository = Depends(get_product_repository)
) -> GetProductByIdQueryHandler:
    """Obtener handler de query por ID"""
    return GetProductByIdQueryHandler(product_repository)


def get_product_by_name_handler(
    product_repository: SQLAlchemyProductRepository = Depends(get_product_repository)
) -> GetProductByNameQueryHandler:
    """Obtener handler de query por nombre"""
    return GetProductByNameQueryHandler(product_repository)


def get_all_products_handler(
    product_repository: SQLAlchemyProductRepository = Depends(get_product_repository)
) -> GetAllProductsQueryHandler:
    """Obtener handler de query de todos los productos"""
    return GetAllProductsQueryHandler(product_repository)


def get_product_stock_handler(
    product_repository: SQLAlchemyProductRepository = Depends(get_product_repository)
) -> GetProductStockQueryHandler:
    """Obtener handler de query de stock"""
    return GetProductStockQueryHandler(product_repository)

