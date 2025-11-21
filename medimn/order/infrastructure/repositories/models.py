"""
Modelos de base de datos para Order Service (adaptado para monolito)
"""
import sys
from pathlib import Path

# Agregar path del monolito
monolith_path = Path(__file__).parent.parent.parent.parent.parent
if str(monolith_path) not in sys.path:
    sys.path.insert(0, str(monolith_path))

# Usar Base unificada del monolito
from infrastructure.database import Base

from sqlalchemy import Column, String, Integer, Float, DateTime, JSON
from datetime import datetime


class OrderModel(Base):
    """Modelo de orden en base de datos"""
    __tablename__ = "orders"
    
    id = Column(String, primary_key=True)
    order_number = Column(String, unique=True, index=True)
    items = Column(JSON)  # Lista de items de la orden
    status = Column(String, index=True)
    total = Column(Float, default=0.0)
    reservations = Column(JSON, nullable=True)  # Reservaciones
    eta = Column(JSON, nullable=True)  # ETA como JSON
    client_id = Column(String, nullable=True, index=True)
    vendor_id = Column(String, nullable=True, index=True)
    delivery_address = Column(String, nullable=True)
    delivery_date = Column(DateTime, nullable=True)
    contact_name = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    route_id = Column(String, nullable=True, index=True)
    return_requested = Column(String, default="false")  # Boolean como string para compatibilidad
    return_reason = Column(String, nullable=True)
    return_status = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

