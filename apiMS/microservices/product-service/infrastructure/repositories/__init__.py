"""
Repositorios de infraestructura para productos
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, Boolean, DateTime, Float, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
import sys
from pathlib import Path

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from shared.domain.value_objects import EntityId, Money
from ...domain.entities import Product
from ...domain.value_objects import ProductName, ProductDescription, Stock
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
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)


class SQLAlchemyProductRepository(IProductRepository):
    """Repositorio de productos con SQLAlchemy"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _to_domain(self, model: ProductModel) -> Product:
        """Convertir modelo de DB a entidad de dominio"""
        return Product(
            product_id=EntityId(model.id),
            name=ProductName(model.name),
            price=Money(model.price),
            description=ProductDescription(model.description) if model.description else None,
            stock=Stock(model.stock),
            is_active=model.is_active
        )
    
    def _to_model(self, product: Product) -> ProductModel:
        """Convertir entidad de dominio a modelo de DB"""
        return ProductModel(
            id=str(product.id),
            name=str(product.name),
            description=str(product.description) if product.description else None,
            price=product.price.amount,
            stock=product.stock.quantity,
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
    
    async def find_all(self, active_only: bool = True) -> List[Product]:
        """Listar todos los productos"""
        query = self.db.query(ProductModel)
        
        if active_only:
            query = query.filter(ProductModel.is_active == True)
        
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

