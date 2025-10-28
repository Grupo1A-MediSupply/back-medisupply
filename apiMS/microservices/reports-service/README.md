# Reports Service

Microservicio de generación de reportes para MediSupply.

## 📋 Endpoints

### GET /api/reports/orders-by-status
Reporte de órdenes agrupadas por estado.

**Response:** Lista con count y percentage por estado

### GET /api/reports/orders-by-month
Reporte de órdenes agrupadas por mes.

**Response:** Lista con orders_count y total_revenue por mes

### GET /api/reports/inventory-status
Reporte del estado actual del inventario.

**Response:** Totales de items, activos, bajo stock, sin stock y por categoría

### GET /api/reports/returns
Reporte de devoluciones de pedidos.

**Response:** Totales y agrupados por status

## 🏗️ Arquitectura

- **API**: Endpoints REST
- **Infraestructura**: Configuración y adaptadores
- **Patrón**: CQRS para queries de reportes

## 🚀 Iniciar

```bash
cd reports-service
python -m uvicorn main:app --host 0.0.0.0 --port 8006
```

