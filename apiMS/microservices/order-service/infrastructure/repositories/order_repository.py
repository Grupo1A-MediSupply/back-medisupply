"""
Repositorio SQLAlchemy para órdenes
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json

from .models import OrderModel
from ...domain.entities import Order
from ...domain.value_objects import EntityId, OrderItem, OrderStatus
from ...domain.ports import IOrderRepository


class SQLAlchemyOrderRepository(IOrderRepository):
    """Implementación de repositorio de órdenes con SQLAlchemy"""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def save(self, order: Order) -> Order:
        """Guardar orden"""
        # Convertir entity a model
        order_model = self.session.query(OrderModel).filter(
            OrderModel.id == str(order.id)
        ).first()
        
        if order_model:
            # Actualizar existente
            order_model.items = [item.to_dict() for item in order.items]
            order_model.status = order.status.value
            order_model.total = order.calculate_total()
            order_model.reservations = order.reservations
            order_model.updated_at = datetime.utcnow()
        else:
            # Crear nuevo
            order_model = OrderModel(
                id=str(order.id),
                items=[item.to_dict() for item in order.items],
                status=order.status.value,
                total=order.calculate_total(),
                reservations=order.reservations
            )
            self.session.add(order_model)
        
        self.session.commit()
        self.session.refresh(order_model)
        
        # Retornar la entidad actualizada
        items = [OrderItem(**item) for item in order_model.items]
        return Order(
            order_id=EntityId(order_model.id),
            items=items,
            status=OrderStatus(order_model.status),
            reservations=order_model.reservations
        )
    
    async def find_by_id(self, order_id: EntityId) -> Optional[Order]:
        """Buscar orden por ID"""
        order_model = self.session.query(OrderModel).filter(
            OrderModel.id == str(order_id)
        ).first()
        
        if not order_model:
            return None
        
        # Convertir model a entity
        items = [OrderItem(**item) for item in order_model.items]
        
        return Order(
            order_id=EntityId(order_model.id),
            items=items,
            status=OrderStatus(order_model.status),
            reservations=order_model.reservations
        )
    
    async def find_by_status(self, status: OrderStatus) -> List[Order]:
        """Buscar órdenes por estado"""
        order_models = self.session.query(OrderModel).filter(
            OrderModel.status == status.value
        ).all()
        
        orders = []
        for model in order_models:
            items = [OrderItem(**item) for item in model.items]
            orders.append(Order(
                order_id=EntityId(model.id),
                items=items,
                status=OrderStatus(model.status),
                reservations=model.reservations
            ))
        
        return orders
    
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[Order]:
        """Obtener todas las órdenes"""
        order_models = self.session.query(OrderModel).offset(skip).limit(limit).all()
        
        orders = []
        for model in order_models:
            items = [OrderItem(**item) for item in model.items]
            orders.append(Order(
                order_id=EntityId(model.id),
                items=items,
                status=OrderStatus(model.status),
                reservations=model.reservations
            ))
        
        return orders
    
    async def delete(self, order_id: EntityId) -> bool:
        """Eliminar orden"""
        order_model = self.session.query(OrderModel).filter(
            OrderModel.id == str(order_id)
        ).first()
        
        if order_model:
            self.session.delete(order_model)
            self.session.commit()
            return True
        
        return False
    
    async def exists_by_id(self, order_id: EntityId) -> bool:
        """Verificar si existe una orden con ese ID"""
        count = self.session.query(OrderModel).filter(
            OrderModel.id == str(order_id)
        ).count()
        
        return count > 0

