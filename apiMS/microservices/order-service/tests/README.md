# Tests del Microservicio de Órdenes

Este directorio contiene todos los tests del microservicio de órdenes.

## Estructura

```
tests/
├── __init__.py
├── conftest.py            # Configuración pytest y fixtures
├── unit/                  # Tests unitarios
│   ├── __init__.py
│   ├── test_entities.py           # Tests de entidades de dominio
│   ├── test_handlers.py           # Tests de command/query handlers
│   ├── test_repository.py         # Tests del repositorio
│   ├── test_value_objects.py      # Tests de value objects
│   ├── test_order_domain_logic.py  # Tests de lógica de dominio
│   ├── test_domain_events.py      # Tests de eventos de dominio
│   └── test_commands_queries.py   # Tests de comandos y queries
└── integration/           # Tests de integración
    └── __init__.py
```

## Tests Unitarios

### test_entities.py
Tests para la entidad principal `Order` y sus métodos:
- ✅ Creación de órdenes
- ✅ Validaciones de negocio
- ✅ Cálculo de totales
- ✅ Gestión de items
- ✅ Transiciones de estado
- ✅ Gestión de reservas
- ✅ Establecimiento de ETA

### test_handlers.py
Tests para los handlers de comandos y queries:
- ✅ Handler de creación de órdenes
- ✅ Handler de confirmación
- ✅ Handler de cancelación
- ✅ Handler de búsqueda por ID
- ✅ Manejo de errores
- ✅ Validaciones de estado

### test_repository.py
Tests para el repositorio SQLAlchemy:
- ✅ Guardar órdenes
- ✅ Buscar por ID
- ✅ Buscar por estado
- ✅ Listar todas
- ✅ Actualizar órdenes
- ✅ Eliminar órdenes
- ✅ Gestión de items y reservas
- ✅ Paginación

### test_value_objects.py
Tests para value objects (OrderItem, ETA):
- ✅ Validaciones de OrderItem
- ✅ Cálculo de subtotales
- ✅ Validaciones de ETA
- ✅ Conversión a diccionarios

### test_order_domain_logic.py
Tests específicos de la lógica de negocio:
- ✅ Máquina de estados
- ✅ Restricciones de transición
- ✅ Gestión de items (combinar duplicados)
- ✅ Actualización de totales
- ✅ Validaciones de negocio

### test_domain_events.py
Tests para eventos de dominio:
- ✅ Emisión de eventos
- ✅ Limpieza de eventos
- ✅ Factory methods

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
pytest tests/unit/test_entities.py::test_create_order_with_items -v
```

### Con verbose
```bash
pytest tests/ -v
```

### Con más detalles
```bash
pytest tests/ -vv
```

## Fixtures

El archivo `conftest.py` proporciona fixtures reutilizables:

- `db_session`: Sesión de base de datos para tests
- `order_repository`: Repositorio de órdenes configurado

## Cobertura Actual

- ✅ **Entidades**: >90%
- ✅ **Handlers**: >80%
- ✅ **Repositorio**: >85%
- ✅ **Value Objects**: >95%
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
- [ ] Tests de seguridad

