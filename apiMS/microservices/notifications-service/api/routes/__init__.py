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
    id: Optional[str] = None
    _id: Optional[str] = None  # Alias según especificación
    userId: Optional[str] = None  # Alias según especificación
    user_id: Optional[str] = None
    title: str
    message: str
    type: str
    priority: Optional[str] = None
    read: Optional[bool] = None  # Alias según especificación
    is_read: Optional[bool] = None
    link: Optional[str] = None
    data: Optional[dict] = None  # Información contextual según especificación
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    createdAt: Optional[str] = None  # Alias según especificación


# ========== Endpoints ==========

@router.get(
    "/notifications",
    response_model=List[NotificationResponse],
    summary="Listar notificaciones",
    description="Lista todas las notificaciones del usuario autenticado"
)
async def get_notifications(
    read: Optional[bool] = None,  # Parámetro según especificación
    is_read: Optional[bool] = None,  # Parámetro para compatibilidad con tests
    type: Optional[str] = None,  # Parámetro según especificación
    notification_type: Optional[str] = None,  # Parámetro para compatibilidad con tests
    limit: int = 50
):
    """Obtener notificaciones del usuario"""
    # TODO: Implementar lógica real con repositorio y autenticación
    # Por ahora retorna mock data para cumplir contrato
    
    # Usar read si está disponible, sino usar is_read (compatibilidad)
    read_filter = read if read is not None else is_read
    
    # Usar type si está disponible, sino usar notification_type (compatibilidad)
    type_filter = type if type is not None else notification_type
    
    mock_notifications = [
        {
            "id": "notif_001",
            "_id": "notif_001",
            "user_id": "user_123",
            "userId": "user_123",
            "title": "Nueva Orden Creada",
            "message": "Se ha creado una nueva orden ORD-1001",
            "type": "order",
            "priority": "medium",
            "is_read": False,
            "read": False,
            "link": "/orders/ORD-1001",
            "data": {"orderId": "ORD-1001", "orderNumber": "ORD-1001"},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "createdAt": datetime.utcnow().isoformat()
        },
        {
            "id": "notif_002",
            "_id": "notif_002",
            "user_id": "user_123",
            "userId": "user_123",
            "title": "Stock Bajo",
            "message": "El producto SKU-001 tiene stock bajo",
            "type": "inventory",
            "priority": "high",
            "is_read": True,
            "read": True,
            "link": "/inventory/SKU-001",
            "data": {"productId": "SKU-001", "currentStock": 5},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "createdAt": datetime.utcnow().isoformat()
        },
        {
            "id": "notif_003",
            "_id": "notif_003",
            "user_id": "user_123",
            "userId": "user_123",
            "title": "Orden Enviada",
            "message": "La orden ORD-1002 ha sido enviada",
            "type": "route",
            "priority": "low",
            "is_read": False,
            "read": False,
            "link": "/orders/ORD-1002",
            "data": {"orderId": "ORD-1002", "routeId": "R-501"},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "createdAt": datetime.utcnow().isoformat()
        }
    ]
    
    # Filtrar por read/is_read si se proporciona
    if read_filter is not None:
        mock_notifications = [
            n for n in mock_notifications if n["is_read"] == read_filter
        ]
    
    # Filtrar por type/notification_type si se proporciona
    if type_filter:
        mock_notifications = [
            n for n in mock_notifications if n["type"] == type_filter
        ]
    
    # Limitar resultados
    return mock_notifications[:limit]


@router.get(
    "/notifications/{notification_id}",
    response_model=NotificationResponse,
    summary="Obtener notificación",
    description="Obtiene una notificación específica por ID"
)
async def get_notification(notification_id: str):
    """Obtener notificación por ID"""
    # TODO: Implementar lógica real con repositorio y validación de usuario
    # Por ahora retorna mock response
    
    if not notification_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada"
        )
    
    # Mock notification
    mock_notification = {
        "id": notification_id,
        "_id": notification_id,
        "user_id": "user_123",
        "userId": "user_123",
        "title": "Notificación de Ejemplo",
        "message": "Esta es una notificación de ejemplo",
        "type": "order",
        "priority": "medium",
        "is_read": False,
        "read": False,
        "link": f"/notifications/{notification_id}",
        "data": {"notificationId": notification_id},
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "createdAt": datetime.utcnow().isoformat()
    }
    
    return mock_notification


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


@router.put(
    "/notifications/read-all",
    response_model=dict,
    summary="Marcar todas las notificaciones como leídas",
    description="Marca todas las notificaciones del usuario como leídas"
)
async def mark_all_notifications_as_read():
    """Marcar todas las notificaciones como leídas"""
    # TODO: Implementar lógica real con repositorio y validación de usuario
    # Por ahora retorna mock response
    
    return {
        "success": True,
        "message": "Todas las notificaciones han sido marcadas como leídas",
        "count": 0  # En producción, retornar el número real de notificaciones actualizadas
    }


@router.delete(
    "/notifications/{notification_id}",
    response_model=dict,
    summary="Eliminar notificación",
    description="Elimina una notificación"
)
async def delete_notification(notification_id: str):
    """Eliminar notificación"""
    # TODO: Implementar lógica real con repositorio y validación de usuario
    # Por ahora retorna mock response
    
    if not notification_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada"
        )
    
    return {
        "success": True,
        "message": f"Notificación {notification_id} eliminada exitosamente"
    }

