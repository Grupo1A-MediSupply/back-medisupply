# Tests Unitarios - Monolito MediSupply

## 📋 Descripción

Suite completa de tests unitarios para el monolito MediSupply con cobertura superior al 70%.

## 🏗️ Estructura

```
tests/
├── __init__.py
├── conftest.py              # Fixtures compartidas
└── unit/                    # Tests unitarios
    ├── __init__.py
    ├── test_auth_handlers.py
    ├── test_auth_adapters.py
    ├── test_auth_repositories.py
    ├── test_auth_services.py
    ├── test_product_handlers.py
    ├── test_product_entities.py
    ├── test_order_handlers.py
    ├── test_value_objects.py
    ├── test_domain_entities.py
    ├── test_infrastructure_config.py
    ├── test_infrastructure_database.py
    └── test_shared_entity.py
```

## 🚀 Ejecución

### Ejecutar todos los tests
```bash
pytest tests/unit/ -v
```

### Ejecutar con cobertura
```bash
pytest tests/unit/ -v --cov=. --cov-report=term-missing --cov-report=html
```

### Ejecutar un archivo específico
```bash
pytest tests/unit/test_auth_handlers.py -v
```

### Ejecutar un test específico
```bash
pytest tests/unit/test_auth_handlers.py::TestRegisterUserCommandHandler::test_register_user_success -v
```

## 📊 Cobertura

La configuración de pytest está configurada para requerir una cobertura mínima del 70%.

### Ver reporte HTML
```bash
open htmlcov/index.html
```

## 📝 Tests Incluidos

### Auth Service
- ✅ Handlers (Register, Login, ChangePassword, etc.)
- ✅ Adapters (Password Hasher, Token Service)
- ✅ Repositories (SQLAlchemy)
- ✅ Services (Event Handlers)

### Product Service
- ✅ Handlers (Create, Update, Get)
- ✅ Entities (Product, Batch)

### Order Service
- ✅ Handlers (Create Order)

### Infrastructure
- ✅ Config (Settings)
- ✅ Database (Base, Session)

### Domain
- ✅ Entities (User, Product)
- ✅ Value Objects (Email, Money, Username, etc.)

### Shared
- ✅ Entity (Base Entity)
- ✅ Value Objects (EntityId, Money)

## 🔧 Configuración

### pytest.ini
- Configuración de pytest con markers y opciones de cobertura
- Requiere cobertura mínima del 70%

### .coveragerc
- Configuración de coverage
- Excluye archivos de tests y migraciones
- Genera reportes HTML y XML

## 📦 Dependencias

Las dependencias de testing están en `requirements.txt`:
- pytest
- pytest-asyncio
- pytest-cov
- pytest-mock
- coverage

## 🎯 Objetivo

Mantener una cobertura de código superior al 70% para garantizar la calidad del código y facilitar el mantenimiento.

