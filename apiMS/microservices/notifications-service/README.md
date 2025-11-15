# Notifications Service

Microservicio de gestión de notificaciones para MediSupply.

## 📋 Endpoints

### GET /api/notifications
Lista todas las notificaciones del usuario autenticado.

**Query Parameters:**
- `is_read` (bool): Filtrar por leídas/no leídas
- `notification_type` (str): Filtrar por tipo (order, shipment, inventory, system)
- `limit` (int): Límite de resultados (default: 50)

**Response:** Lista de notificaciones

### PUT /api/notifications/{notification_id}/read
Marca una notificación como leída.

**Response:** Confirmación de éxito

## 🏗️ Arquitectura

- **Dominio**: Notification entity, NotificationType, NotificationPriority
- **Aplicación**: Commands y Queries con CQRS
- **Infraestructura**: Configuración y repositorio
- **API**: FastAPI con endpoints REST

## 🚀 Iniciar

```bash
cd notifications-service
python -m uvicorn main:app --host 0.0.0.0 --port 8007
```

## 📦 Estructura

```
notifications-service/
├── domain/          # Notification entity y types
├── application/     # Commands, queries, handlers
├── infrastructure/  # Repositorio, database, config
├── api/            # Rutas y dependencies
├── tests/          # Pruebas
└── main.py         # Entry point
```

## 🎯 Tipos de Notificaciones

- **order**: Notificaciones de órdenes
- **shipment**: Notificaciones de envíos
- **inventory**: Notificaciones de inventario
- **system**: Notificaciones del sistema

## 🔔 Prioridades

- **low**: Prioridad baja
- **medium**: Prioridad media
- **high**: Prioridad alta
- **urgent**: Urgente

