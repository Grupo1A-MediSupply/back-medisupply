"""
Queries del servicio de órdenes
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class GetOrderByIdQuery:
    """Query para obtener una orden por ID"""
    order_id: str


@dataclass
class GetOrdersByStatusQuery:
    """Query para obtener órdenes por estado"""
    status: str
    skip: int = 0
    limit: int = 100


@dataclass
class GetAllOrdersQuery:
    """Query para obtener todas las órdenes"""
    skip: int = 0
    limit: int = 100
    status: Optional[str] = None

