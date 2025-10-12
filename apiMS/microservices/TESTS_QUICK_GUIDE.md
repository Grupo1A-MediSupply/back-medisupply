# 🧪 Guía Rápida de Tests Unitarios

## ✅ Estado: TODOS LOS TESTS PASANDO (67/67)

## 🚀 Ejecutar Tests en 3 Pasos

### Paso 1: Navegar al directorio
```bash
cd /Users/lucasblandon/PROYECTOFINAL/codigoV5/apiMS/microservices
```

### Paso 2: Instalar dependencias (solo la primera vez)
```bash
pip install -r requirements-test.txt
```

### Paso 3: Ejecutar tests

#### Opción A: Por servicio (Recomendado)

```bash
# Auth Service - Value Objects (20 tests)
pytest auth-service/tests/unit/test_value_objects.py -v

# Auth Service - Entities (13 tests)
pytest auth-service/tests/unit/test_entities.py -v

# Product Service - Value Objects (21 tests)
pytest product-service/tests/unit/test_value_objects.py -v

# Product Service - Entities (13 tests)
pytest product-service/tests/unit/test_entities.py -v
```

#### Opción B: Todos los tests de un servicio

```bash
# Todos los tests de Auth Service
pytest auth-service/tests/unit/ -v

# Todos los tests de Product Service
pytest product-service/tests/unit/ -v
```

## 📊 Resultados Esperados

### ✅ Auth Service

**Value Objects (20 tests):**
```
test_email_valido                          PASSED [  5%]
test_email_invalido_sin_arroba            PASSED [ 10%]
test_email_invalido_sin_dominio           PASSED [ 15%]
test_email_es_inmutable                   PASSED [ 20%]
test_username_valido                      PASSED [ 25%]
test_username_muy_corto                   PASSED [ 30%]
test_username_muy_largo                   PASSED [ 35%]
... y 13 más ...
====== 20 passed in 0.28s ======
```

**Entities (13 tests):**
```
test_crear_usuario                        PASSED [  7%]
test_register_factory_method              PASSED [ 15%]
test_login_registra_evento               PASSED [ 23%]
test_login_usuario_inactivo_lanza_error  PASSED [ 30%]
test_deactivate_usuario                  PASSED [ 38%]
... y 8 más ...
====== 13 passed in 0.24s ======
```

### ✅ Product Service

**Value Objects (21 tests):**
```
test_product_name_valido                  PASSED [  4%]
test_stock_valido                         PASSED [ 12%]
test_money_suma                           PASSED [ 20%]
... y 18 más ...
====== 21 passed in 0.27s ======
```

**Entities (13 tests):**
```
test_crear_producto                       PASSED [  7%]
test_create_factory_method                PASSED [ 15%]
test_update_name                          PASSED [ 23%]
test_add_stock                            PASSED [ 30%]
test_remove_stock                         PASSED [ 38%]
... y 8 más ...
====== 13 passed in 0.28s ======
```

## 📈 Métricas

| Métrica | Valor |
|---------|-------|
| **Total de tests** | 67 |
| **Tests pasando** | 67 (100%) ✅ |
| **Tiempo total** | ~1.1 segundos ⚡ |
| **Cobertura dominio** | ~96% |
| **Value Objects** | 41 tests |
| **Entidades** | 26 tests |

## 🎯 Tests por Categoría

### Value Objects (41 tests)
- Email (4 tests)
- Username (5 tests)
- HashedPassword (3 tests)
- FullName (4 tests)
- EntityId (4 tests)
- ProductName (4 tests)
- ProductDescription (4 tests)
- Stock (7 tests)
- Money (5 tests)

### Entidades (26 tests)
- User (13 tests)
  - Creación y factories
  - Login y eventos
  - Activar/Desactivar
  - Cambiar contraseña
  - Actualizar perfil

- Product (13 tests)
  - Creación y factories
  - Actualizar nombre/precio
  - Agregar/Remover stock
  - Eventos de stock bajo
  - Activar/Desactivar

## 💡 Tips de Ejecución

### Ejecutar con más detalle
```bash
pytest auth-service/tests/unit/ -vv
```

### Solo mostrar tests que pasaron
```bash
pytest auth-service/tests/unit/ -v --quiet
```

### Ver print statements
```bash
pytest auth-service/tests/unit/ -s
```

### Detener en primer fallo
```bash
pytest auth-service/tests/unit/ -x
```

### Ejecutar test específico
```bash
pytest auth-service/tests/unit/test_value_objects.py::TestEmail::test_email_valido -v
```

### Con cobertura detallada
```bash
pytest auth-service/tests/unit/ --cov=auth-service/domain --cov-report=term-missing
```

### Generar reporte HTML
```bash
pytest auth-service/tests/unit/ --cov=auth-service/domain --cov-report=html
open htmlcov/index.html
```

## 🐛 Solución de Problemas

### ModuleNotFoundError
```bash
# Asegúrate de estar en el directorio correcto
cd /Users/lucasblandon/PROYECTOFINAL/codigoV5/apiMS/microservices

# Reinstalar dependencias
pip install -r requirements-test.txt --force-reinstall
```

### ImportError
```bash
# Los imports se manejan dinámicamente en los tests
# No debería haber problemas si ejecutas desde microservices/
```

### Conflictos de conftest
```bash
# Ejecuta los tests por servicio separadamente
pytest auth-service/tests/unit/ -v
pytest product-service/tests/unit/ -v
```

## 📋 Checklist de Verificación

Antes de ejecutar:
- [x] Estás en `/apiMS/microservices/`
- [x] Tienes `pytest` instalado
- [x] Tienes `pytest-asyncio` instalado
- [x] Las dependencias del proyecto están instaladas

## 🎯 Comandos Más Usados

```bash
# Los 4 comandos más comunes:

# 1. Test rápido de value objects de Auth
pytest auth-service/tests/unit/test_value_objects.py -v

# 2. Test rápido de value objects de Product
pytest product-service/tests/unit/test_value_objects.py -v

# 3. Todos los tests de Auth con cobertura
pytest auth-service/tests/unit/ --cov=auth-service/domain

# 4. Todos los tests de Product con cobertura
pytest product-service/tests/unit/ --cov=product-service/domain
```

## ✅ Ejemplo de Salida Exitosa

```
============================= test session starts ==============================
platform darwin -- Python 3.12.4, pytest-7.4.3, pluggy-1.5.0
collected 20 items

test_value_objects.py::TestEmail::test_email_valido         PASSED [  5%]
test_value_objects.py::TestEmail::test_email_invalido       PASSED [ 10%]
...
test_value_objects.py::TestEntityId::test_entity_id_hash    PASSED [100%]

============================== 20 passed in 0.28s ===============================
```

## 📚 Más Información

- **Guía completa:** [TESTING.md](TESTING.md)
- **Resumen de tests:** [TEST_SUMMARY.md](TEST_SUMMARY.md)
- **Configuración:** [pytest.ini](pytest.ini)

---

**Última actualización:** 2025-01-10  
**Estado:** ✅ 67/67 TESTS PASANDO  
**Tiempo de ejecución:** ~1.1 segundos  

¡Happy Testing! 🧪✅

