# Tests del Microservicio de Logística

Este directorio contiene todos los tests del microservicio de logística.

## Estructura

```
tests/
├── __init__.py
├── conftest.py              # Configuración pytest y fixtures
├── unit/                    # Tests unitarios
│   ├── __init__.py
│   ├── test_entities.py                # Tests de entidades
│   ├── test_handlers.py                # Tests de handlers
│   ├── test_repository.py              # Tests del repositorio
│   ├── test_value_objects.py            # Tests de value objects
│   ├── test_route_domain_logic.py    # Tests de lógica de dominio
│   └── test_commands_queries.py       # Tests de comandos y queries
└── integration/             # Tests de integración
    └── __init__.py
```

## Tests Unitarios

### test_entities.py
Tests para la entidad principal `Route` y sus métodos:
- ✅ Creación de rutas
- ✅ Validaciones de negocio
- ✅ Gestión de paradas
- ✅ Transiciones de estado
- ✅ Value Objects (Position, Stop, ETA)

### test_handlers.py
Tests para los handlers de comandos y queries:
- ✅ Handler de creación de rutas
- ✅ Handler de inicio de rutas
- ✅ Handler de obtención por ID
- ✅ Manejo de errores

### test_repository.py
Tests para el repositorio SQLAlchemy:
- ✅ Guardar rutas
- ✅ Buscar por ID
- ✅ Buscar por vehículo
- ✅ Buscar por estado
- ✅ Listar todas
- ✅ Actualizar rutas
- ✅ Eliminar rutas
- ✅ Paginación

### test_value_objects.py
Tests para value objects (Stop, Position, ETA):
- ✅ Validaciones de Stop
- ✅ Validaciones de Position (GPS)
- ✅ Validaciones de ETA
- ✅ Conversión a diccionarios

### test_route_domain_logic.py
Tests específicos de la lógica de negocio:
- ✅ Máquina de estados
- ✅ Restricciones de transición
- ✅ Gestión de paradas (agregar/remover)
- ✅ Ordenamiento por prioridad
- ✅ Validaciones de negocio

### test_commands_queries.py
Tests para comandos y queries (data classes):
- ✅ Creación de comandos
- ✅ Creación de queries
- ✅ Valores por defecto

## Ejecutar Tests

### Todos los tests
```bash
pytest tests/
```

### Tests unitarios específicos
```bash
pytest tests/unit/test_entities.py
pytest tests/unit/test_repository.py
pytest tests/unit/test_handlers.py
```

### Con cobertura
```bash
pytest tests/ --cov=. --cov-report=html
```

### Test específico
```bash
pytest tests/unit/test_entities.py::test_create_route_with_stops -v
```

### Con verbose
```bash
pytest tests/ -v
```

## Fixtures

El archivo `conftest.py` proporciona fixtures reutilizables:

- `db_session`: Sesión de base de datos para tests
- `logistics_repository`: Repositorio de logística configurado

## Cobertura Estimada

- ✅ **Entidades**: >95%
- ✅ **Handlers**: >80%
- ✅ **Repositorio**: >85%
- ✅ **Value Objects**: 100%
- ✅ **Lógica de Dominio**: >90%
- ✅ **Commands/Queries**: 100%

## Mejores Prácticas

1. **Aislamiento**: Cada test es independiente
2. **Naming**: Nombres descriptivos que explican el test
3. **AAA Pattern**: Arrange, Act, Assert
4. **Fixtures**: Uso de fixtures para setup/teardown
5. **Mock**: Uso de mocks para dependencias externas
6. **Async**: Tests async marcados con `@pytest.mark.asyncio`

## Próximos Tests a Agregar

- [ ] Tests de integración con la API
- [ ] Tests de integración con base de datos
- [ ] Tests E2E completos
- [ ] Tests de rendimiento
- [ ] Tests de concurrencia
- [ ] Tests de tracking en tiempo real

