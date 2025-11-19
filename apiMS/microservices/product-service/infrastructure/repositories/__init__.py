"""
Repositorios de infraestructura para productos
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, Boolean, DateTime, Float, Integer, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
import sys
from pathlib import Path
import json

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from shared.domain.value_objects import EntityId, Money
from ...domain.entities import Product, Batch
from ...domain.value_objects import (
    ProductName, ProductDescription, Stock, Lot, Warehouse, 
    Supplier, Category, VendorId
)
from ...domain.ports import IProductRepository

Base = declarative_base()


class ProductModel(Base):
    """Modelo de base de datos para Product"""
    __tablename__ = "products"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    expiry = Column(DateTime, nullable=True)
    lot = Column(String, nullable=True)
    warehouse = Column(String, nullable=True)
    supplier = Column(String, nullable=True)
    category = Column(String, nullable=True, index=True)
    batches = Column(JSON, nullable=True)  # Array de batches como JSON
    vendor_id = Column(String, nullable=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)


class SQLAlchemyProductRepository(IProductRepository):
    """Repositorio de productos con SQLAlchemy"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _to_domain(self, model: ProductModel) -> Product:
        """Convertir modelo de DB a entidad de dominio"""
        # Convertir batches de JSON a objetos Batch
        batches = []
        if model.batches:
            try:
                batches_data = json.loads(model.batches) if isinstance(model.batches, str) else model.batches
                for batch_data in batches_data:
                    batches.append(Batch(
                        batch=batch_data.get("batch", ""),
                        quantity=batch_data.get("quantity", 0),
                        expiry=datetime.fromisoformat(batch_data["expiry"]) if batch_data.get("expiry") else None,
                        location=batch_data.get("location")
                    ))
            except (json.JSONDecodeError, ValueError, KeyError):
                batches = []
        
        return Product(
            product_id=EntityId(model.id),
            name=ProductName(model.name),
            price=Money(model.price),
            description=ProductDescription(model.description) if model.description else None,
            stock=Stock(model.stock),
            expiry=model.expiry,
            lot=Lot(model.lot) if model.lot else None,
            warehouse=Warehouse(model.warehouse) if model.warehouse else None,
            supplier=Supplier(model.supplier) if model.supplier else None,
            category=Category(model.category) if model.category else None,
            batches=batches,
            vendor_id=VendorId(model.vendor_id) if model.vendor_id else None,
            is_active=model.is_active
        )
    
    def _to_model(self, product: Product) -> ProductModel:
        """Convertir entidad de dominio a modelo de DB"""
        # Convertir batches a JSON
        batches_json = None
        if product.batches:
            batches_json = json.dumps([batch.to_dict() for batch in product.batches])
        
        return ProductModel(
            id=str(product.id),
            name=str(product.name),
            description=str(product.description) if product.description else None,
            price=product.price.amount,
            stock=product.stock.quantity,
            expiry=product.expiry,
            lot=str(product.lot) if product.lot else None,
            warehouse=str(product.warehouse) if product.warehouse else None,
            supplier=str(product.supplier) if product.supplier else None,
            category=str(product.category) if product.category else None,
            batches=batches_json,
            vendor_id=str(product.vendor_id) if product.vendor_id else None,
            is_active=product.is_active,
            created_at=product.created_at,
            updated_at=product.updated_at
        )
    
    async def save(self, product: Product) -> Product:
        """Guardar producto"""
        # Buscar si existe
        existing = self.db.query(ProductModel).filter(
            ProductModel.id == str(product.id)
        ).first()
        
        if existing:
            # Actualizar
            existing.name = str(product.name)
            existing.description = str(product.description) if product.description else None
            existing.price = product.price.amount
            existing.stock = product.stock.quantity
            existing.expiry = product.expiry
            existing.lot = str(product.lot) if product.lot else None
            existing.warehouse = str(product.warehouse) if product.warehouse else None
            existing.supplier = str(product.supplier) if product.supplier else None
            existing.category = str(product.category) if product.category else None
            existing.batches = json.dumps([batch.to_dict() for batch in product.batches]) if product.batches else None
            existing.vendor_id = str(product.vendor_id) if product.vendor_id else None
            existing.is_active = product.is_active
            existing.updated_at = product.updated_at
        else:
            # Crear nuevo
            model = self._to_model(product)
            self.db.add(model)
        
        self.db.commit()
        
        # Refrescar
        model = self.db.query(ProductModel).filter(
            ProductModel.id == str(product.id)
        ).first()
        
        return self._to_domain(model)
    
    async def find_by_id(self, product_id: EntityId) -> Optional[Product]:
        """Buscar producto por ID"""
        model = self.db.query(ProductModel).filter(
            ProductModel.id == str(product_id)
        ).first()
        
        return self._to_domain(model) if model else None
    
    async def find_by_name(self, name: ProductName) -> Optional[Product]:
        """Buscar producto por nombre"""
        model = self.db.query(ProductModel).filter(
            ProductModel.name == str(name)
        ).first()
        
        return self._to_domain(model) if model else None
    
    async def find_all(self, active_only: bool = True, search: Optional[str] = None, 
                      category: Optional[str] = None, low_stock_only: bool = False) -> List[Product]:
        """Listar todos los productos"""
        query = self.db.query(ProductModel)
        
        if active_only:
            query = query.filter(ProductModel.is_active == True)
        
        if search:
            query = query.filter(
                ProductModel.name.ilike(f"%{search}%") |
                (ProductModel.description.ilike(f"%{search}%") if ProductModel.description else False)
            )
        
        if category:
            query = query.filter(ProductModel.category == category)
        
        if low_stock_only:
            query = query.filter(ProductModel.stock <= 10)  # LOW_STOCK_THRESHOLD
        
        models = query.all()
        
        return [self._to_domain(model) for model in models]
    
    async def delete(self, product_id: EntityId) -> bool:
        """Eliminar producto"""
        model = self.db.query(ProductModel).filter(
            ProductModel.id == str(product_id)
        ).first()
        
        if model:
            self.db.delete(model)
            self.db.commit()
            return True
        
        return False
    
    async def exists_by_id(self, product_id: EntityId) -> bool:
        """Verificar si existe producto con ese ID"""
        count = self.db.query(ProductModel).filter(
            ProductModel.id == str(product_id)
        ).count()
        
        return count > 0

