# Inventory Service

Microservicio de gestión de inventario para MediSupply.

## 📋 Endpoints

### GET /api/inventory
Lista todos los items de inventario.

**Query Parameters:**
- `active_only` (bool): Solo items activos
- `low_stock_only` (bool): Solo items con stock bajo
- `category` (str): Filtrar por categoría

**Response:** Lista de items de inventario

### POST /api/inventory/upload
Sube un archivo CSV para importar items masivamente.

**Body:** Multipart form con archivo CSV

**Response:** Resumen de importación

### GET /api/inventory/template
Descarga un template CSV para importar items.

**Response:** CSV file download

## 🏗️ Arquitectura

- **Dominio**: InventoryItem, Value Objects (SKU, Stock, Location)
- **Aplicación**: Commands y Queries con CQRS
- **Infraestructura**: Repositorio SQLAlchemy
- **API**: FastAPI con endpoints REST

## 🚀 Iniciar

```bash
cd inventory-service
python -m uvicorn main:app --host 0.0.0.0 --port 8005
```

## 📦 Estructura

```
inventory-service/
├── domain/          # Entidades y value objects
├── application/     # Commands, queries, handlers
├── infrastructure/  # Repositorio, database, config
├── api/            # Rutas y dependencies
├── tests/          # Pruebas
└── main.py         # Entry point
```

