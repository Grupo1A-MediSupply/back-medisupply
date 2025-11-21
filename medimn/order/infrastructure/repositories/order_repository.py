"""
Repositorio SQLAlchemy para órdenes
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json

from .models import OrderModel
from ...domain.entities import Order, OrderItem, ETA, OrderStatus, ReturnStatus
from shared.domain.value_objects import EntityId
from ...domain.ports import IOrderRepository


class SQLAlchemyOrderRepository(IOrderRepository):
    """Implementación de repositorio de órdenes con SQLAlchemy"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def _to_domain(self, model: OrderModel) -> Order:
        """Convertir modelo a entidad de dominio"""
        items = [OrderItem(**item) for item in model.items]
        eta = None
        if model.eta:
            eta_data = json.loads(model.eta) if isinstance(model.eta, str) else model.eta
            eta = ETA(
                date=datetime.fromisoformat(eta_data["date"]) if eta_data.get("date") else datetime.utcnow(),
                window_minutes=eta_data.get("windowMinutes", 0)
            )
        
        return_status = None
        if model.return_status:
            try:
                return_status = ReturnStatus(model.return_status)
            except ValueError:
                return_status = None
        
        return Order(
            order_id=EntityId(model.id),
            items=items,
            status=OrderStatus(model.status),
            reservations=model.reservations or [],
            eta=eta,
            order_number=model.order_number,
            client_id=model.client_id,
            vendor_id=model.vendor_id,
            delivery_address=model.delivery_address,
            delivery_date=model.delivery_date,
            contact_name=model.contact_name,
            contact_phone=model.contact_phone,
            notes=model.notes,
            route_id=model.route_id,
            return_requested=model.return_requested == "true" if isinstance(model.return_requested, str) else bool(model.return_requested),
            return_reason=model.return_reason,
            return_status=return_status
        )
    
    async def save(self, order: Order) -> Order:
        """Guardar orden"""
        # Convertir entity a model
        order_model = self.session.query(OrderModel).filter(
            OrderModel.id == str(order.id)
        ).first()
        
        eta_json = None
        if order.eta:
            eta_json = json.dumps(order.eta.to_dict())
        
        if order_model:
            # Actualizar existente
            order_model.items = [item.to_dict() for item in order.items]
            order_model.status = order.status.value
            order_model.total = order.total_amount
            order_model.reservations = order.reservations
            order_model.eta = eta_json
            order_model.order_number = order.order_number
            order_model.client_id = order.client_id
            order_model.vendor_id = order.vendor_id
            order_model.delivery_address = order.delivery_address
            order_model.delivery_date = order.delivery_date
            order_model.contact_name = order.contact_name
            order_model.contact_phone = order.contact_phone
            order_model.notes = order.notes
            order_model.route_id = order.route_id
            order_model.return_requested = "true" if order.return_requested else "false"
            order_model.return_reason = order.return_reason
            order_model.return_status = order.return_status.value if order.return_status else None
            order_model.updated_at = datetime.utcnow()
        else:
            # Crear nuevo
            order_model = OrderModel(
                id=str(order.id),
                order_number=order.order_number,
                items=[item.to_dict() for item in order.items],
                status=order.status.value,
                total=order.total_amount,
                reservations=order.reservations,
                eta=eta_json,
                client_id=order.client_id,
                vendor_id=order.vendor_id,
                delivery_address=order.delivery_address,
                delivery_date=order.delivery_date,
                contact_name=order.contact_name,
                contact_phone=order.contact_phone,
                notes=order.notes,
                route_id=order.route_id,
                return_requested="true" if order.return_requested else "false",
                return_reason=order.return_reason,
                return_status=order.return_status.value if order.return_status else None
            )
            self.session.add(order_model)
        
        self.session.commit()
        self.session.refresh(order_model)
        
        # Retornar la entidad actualizada
        return self._to_domain(order_model)
    
    async def find_by_id(self, order_id: EntityId) -> Optional[Order]:
        """Buscar orden por ID"""
        order_model = self.session.query(OrderModel).filter(
            OrderModel.id == str(order_id)
        ).first()
        
        if not order_model:
            return None
        
        return self._to_domain(order_model)
    
    async def find_by_status(self, status: OrderStatus) -> List[Order]:
        """Buscar órdenes por estado"""
        order_models = self.session.query(OrderModel).filter(
            OrderModel.status == status.value
        ).all()
        
        return [self._to_domain(model) for model in order_models]
    
    async def find_all(self, skip: int = 0, limit: int = 100, status: Optional[OrderStatus] = None) -> List[Order]:
        """Obtener todas las órdenes"""
        query = self.session.query(OrderModel)
        
        if status:
            query = query.filter(OrderModel.status == status.value)
        
        order_models = query.offset(skip).limit(limit).all()
        
        return [self._to_domain(model) for model in order_models]
    
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

