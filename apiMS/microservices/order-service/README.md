# Order Service

Microservicio de órdenes con arquitectura hexagonal para el proyecto MediSupply.

## Arquitectura

Este microservicio sigue los principios de:
- **Arquitectura Hexagonal** (Ports and Adapters)
- **Domain-Driven Design (DDD)**
- **CQRS** (Command Query Responsibility Segregation)
- **Event-Driven Architecture**

## Estructura

```
order-service/
├── domain/          # Lógica de negocio
│   ├── entities/    # Entidades de dominio
│   ├── value_objects/  # Objetos de valor
│   ├── events/      # Eventos de dominio
│   └── ports/       # Interfaces (contratos)
├── application/     # Casos de uso
│   ├── commands/    # Comandos
│   ├── queries/     # Consultas
│   ├── handlers/    # Handlers de comandos y queries
│   └── services/    # Servicios de aplicación
├── infrastructure/  # Implementaciones técnicas
│   ├── config.py    # Configuración
│   ├── database.py  # Base de datos
│   └── repositories/  # Implementación de repositorios
├── api/            # Capa de API REST
│   ├── dependencies/  # Dependencias
│   └── routes/     # Endpoints
├── tests/          # Tests
└── main.py         # Aplicación FastAPI
```

## Características

- **Gestión de órdenes**: Crear, actualizar, confirmar, cancelar
- **Estados de orden**: PLACED, CONFIRMED, CANCELLED, PICKED, SHIPPED, DELIVERED
- **Gestión de items**: Agregar, remover artículos
- **Reservas**: Vinculación con reservas de inventario
- **ETAs**: Tiempo estimado de llegada
- **Eventos de dominio**: Para integración con otros servicios

## Endpoints

- `POST /api/v1/orders` - Crear orden
- `GET /api/v1/orders/{order_id}` - Obtener orden
- `PUT /api/v1/orders/{order_id}` - Actualizar orden
- `GET /api/v1/orders` - Listar órdenes
- `POST /api/v1/orders/{order_id}/confirm` - Confirmar orden
- `POST /api/v1/orders/{order_id}/cancel` - Cancelar orden

## Ejecución

```bash
# Desarrollo
python run.py

# Producción
python main.py
```

## Docker

```bash
docker build -t order-service .
docker run -p 8003:8003 order-service
```

## Tests

```bash
pytest tests/
```

