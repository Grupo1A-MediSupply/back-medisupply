"""
Modelos de base de datos para Order Service
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class OrderModel(Base):
    """Modelo de orden en base de datos"""
    __tablename__ = "orders"
    
    id = Column(String, primary_key=True)
    items = Column(JSON)  # Lista de items de la orden
    status = Column(String)
    total = Column(Float, default=0.0)
    reservations = Column(JSON, nullable=True)  # Reservaciones
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

