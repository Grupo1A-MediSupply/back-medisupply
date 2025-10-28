"""
Rutas de la API de notificaciones
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()


# ========== Schemas ==========

class NotificationResponse(BaseModel):
    """Response para notificación"""
    id: str
    user_id: str
    title: str
    message: str
    type: str
    priority: str
    is_read: bool
    link: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# ========== Endpoints ==========

@router.get(
    "/notifications",
    response_model=List[NotificationResponse],
    summary="Listar notificaciones",
    description="Lista todas las notificaciones del usuario autenticado"
)
async def get_notifications(
    is_read: Optional[bool] = None,
    notification_type: Optional[str] = None,
    limit: int = 50
):
    """Obtener notificaciones del usuario"""
    # TODO: Implementar lógica real con repositorio y autenticación
    # Por ahora retorna mock data para cumplir contrato
    
    mock_notifications = [
        {
            "id": "notif_001",
            "user_id": "user_123",
            "title": "Nueva Orden Creada",
            "message": "Se ha creado una nueva orden ORD-1001",
            "type": "order",
            "priority": "medium",
            "is_read": False,
            "link": "/orders/ORD-1001",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": "notif_002",
            "user_id": "user_123",
            "title": "Stock Bajo",
            "message": "El producto SKU-001 tiene stock bajo",
            "type": "inventory",
            "priority": "high",
            "is_read": True,
            "link": "/inventory/SKU-001",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": "notif_003",
            "user_id": "user_123",
            "title": "Orden Enviada",
            "message": "La orden ORD-1002 ha sido enviada",
            "type": "shipment",
            "priority": "low",
            "is_read": False,
            "link": "/orders/ORD-1002",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Filtrar por is_read si se proporciona
    if is_read is not None:
        mock_notifications = [
            n for n in mock_notifications if n["is_read"] == is_read
        ]
    
    # Filtrar por type si se proporciona
    if notification_type:
        mock_notifications = [
            n for n in mock_notifications if n["type"] == notification_type
        ]
    
    # Limitar resultados
    return mock_notifications[:limit]


@router.put(
    "/notifications/{notification_id}/read",
    response_model=dict,
    summary="Marcar notificación como leída",
    description="Marca una notificación como leída"
)
async def mark_notification_as_read(notification_id: str):
    """Marcar notificación como leída"""
    # TODO: Implementar lógica real con repositorio y validación de usuario
    # Por ahora retorna mock response
    
    if not notification_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada"
        )
    
    return {
        "success": True,
        "message": f"Notificación {notification_id} marcada como leída"
    }

