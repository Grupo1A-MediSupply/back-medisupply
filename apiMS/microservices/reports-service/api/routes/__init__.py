"""
Rutas de la API de reportes
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

router = APIRouter()


# ========== Schemas ==========

class OrderStatusReport(BaseModel):
    """Reporte de órdenes por estado"""
    status: str
    count: int
    percentage: float


class MonthlyOrderReport(BaseModel):
    """Reporte de órdenes por mes"""
    month: str
    orders_count: int
    total_revenue: float


class InventoryStatusReport(BaseModel):
    """Reporte de estado de inventario"""
    total_items: int
    active_items: int
    low_stock_items: int
    out_of_stock_items: int
    categories: Dict[str, int]


class ReturnsReport(BaseModel):
    """Reporte de devoluciones"""
    total_returns: int
    by_status: Dict[str, int]
    total_refund_amount: float


# ========== Endpoints ==========

@router.get(
    "/reports/orders-by-status",
    response_model=List[OrderStatusReport],
    summary="Reporte de órdenes por estado",
    description="Genera un reporte de órdenes agrupadas por estado"
)
async def get_orders_by_status():
    """Obtener reporte de órdenes por estado"""
    # TODO: Implementar lógica real consultando order-service
    # Por ahora retorna mock data para cumplir contrato
    
    mock_data = [
        {"status": "PLACED", "count": 25, "percentage": 35.7},
        {"status": "CONFIRMED", "count": 18, "percentage": 25.7},
        {"status": "SHIPPED", "count": 15, "percentage": 21.4},
        {"status": "DELIVERED", "count": 12, "percentage": 17.2}
    ]
    
    return mock_data


@router.get(
    "/reports/orders-by-month",
    response_model=List[MonthlyOrderReport],
    summary="Reporte de órdenes por mes",
    description="Genera un reporte de órdenes agrupadas por mes"
)
async def get_orders_by_month():
    """Obtener reporte de órdenes por mes"""
    # TODO: Implementar lógica real consultando order-service
    # Por ahora retorna mock data
    
    mock_data = [
        {"month": "2025-01", "orders_count": 45, "total_revenue": 125000.0},
        {"month": "2025-02", "orders_count": 52, "total_revenue": 148000.0},
        {"month": "2025-03", "orders_count": 38, "total_revenue": 112000.0}
    ]
    
    return mock_data


@router.get(
    "/reports/inventory-status",
    response_model=InventoryStatusReport,
    summary="Reporte de estado de inventario",
    description="Genera un reporte del estado actual del inventario"
)
async def get_inventory_status():
    """Obtener reporte de estado de inventario"""
    # TODO: Implementar lógica real consultando inventory-service y product-service
    # Por ahora retorna mock data
    
    mock_data = {
        "total_items": 150,
        "active_items": 145,
        "low_stock_items": 12,
        "out_of_stock_items": 3,
        "categories": {
            "Suministros Médicos": 45,
            "Equipamiento": 30,
            "Medicamentos": 50,
            "Otros": 25
        }
    }
    
    return mock_data


@router.get(
    "/reports/returns",
    response_model=ReturnsReport,
    summary="Reporte de devoluciones",
    description="Genera un reporte de devoluciones de pedidos"
)
async def get_returns_report():
    """Obtener reporte de devoluciones"""
    # TODO: Implementar lógica real consultando order-service
    # Por ahora retorna mock data
    
    mock_data = {
        "total_returns": 8,
        "by_status": {
            "Pendiente": 3,
            "Aprobada": 4,
            "Rechazada": 1
        },
        "total_refund_amount": 2500.0
    }
    
    return mock_data

