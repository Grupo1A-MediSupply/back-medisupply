# Logistics Service

Microservicio de logística con arquitectura hexagonal para el proyecto MediSupply.

## Arquitectura

Este microservicio sigue los principios de:
- **Arquitectura Hexagonal** (Ports and Adapters)
- **Domain-Driven Design (DDD)**
- **CQRS** (Command Query Responsibility Segregation)
- **Event-Driven Architecture**

## Estructura

```
logistics-service/
├── domain/          # Lógica de negocio
│   ├── entities/    # Route, Stop, Position, ETA, TrackingInfo
│   ├── events/      # Eventos de dominio
│   ├── ports/       # Interfaces
│   └── value_objects/
├── application/     # Casos de uso
│   ├── commands/    # Comandos
│   ├── queries/     # Consultas
│   ├── handlers/    # Handlers
│   └── services/    # Servicios de aplicación
├── infrastructure/  # Implementaciones técnicas
├── api/            # Capa de API REST
└── tests/          # Tests
```

## Características

- **Gestión de rutas**: Crear, iniciar, completar, cancelar
- **Estados de ruta**: PLANNED, IN_PROGRESS, COMPLETED, CANCELLED
- **Gestión de paradas**: Agregar, eliminar paradas
- **Tracking**: Seguimiento de vehículos y rutas
- **Eventos de dominio**: Para integración con otros servicios

## Endpoints

- `POST /api/v1/routes` - Crear ruta
- `GET /api/v1/routes/{route_id}` - Obtener ruta
- `POST /api/v1/routes/{route_id}/start` - Iniciar ruta
- `POST /api/v1/routes/{route_id}/complete` - Completar ruta
- `POST /api/v1/routes/{route_id}/cancel` - Cancelar ruta
- `GET /api/v1/routes` - Listar rutas

## Ejecución

```bash
# Desarrollo
python run.py

# Producción
python main.py
```

## Docker

```bash
docker build -t logistics-service .
docker run -p 8004:8004 logistics-service
```

## Tests

```bash
pytest tests/
```

