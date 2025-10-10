# Changelog

## [1.1.0] - 2025-10-10

### ✨ Nuevas Funcionalidades

#### Gestión de Productos
- **Modelo de Producto**: Añadido modelo `Product` en `models.py` con campos:
  - `id`: Identificador único (UUID)
  - `name`: Nombre del producto
  - `description`: Descripción del producto
  - `price`: Precio (debe ser mayor a 0)
  - `stock`: Stock disponible
  - `is_active`: Estado del producto
  - `created_at`: Fecha de creación
  - `updated_at`: Fecha de actualización

- **Esquemas Pydantic**: Agregados esquemas para validación:
  - `ProductBase`: Modelo base con validaciones
  - `ProductCreate`: Para crear productos
  - `ProductUpdate`: Para actualizar productos (preparado para futuras actualizaciones)
  - `ProductResponse`: Para respuestas de la API

- **Endpoints de Productos**:
  - `GET /api/v1/products`: Lista todos los productos activos
    - Devuelve array JSON con productos
    - Incluye todos los campos del modelo
    - Respuesta 200 OK
  
  - `POST /api/v1/products`: Crea un nuevo producto
    - Valida datos con Pydantic
    - Genera UUID automáticamente
    - Respuesta 201 Created con el producto creado

### 🧪 Pruebas

- **Script de Pruebas Automatizadas**: `test_endpoints.py`
  - Pruebas de autenticación (login válido/inválido)
  - Pruebas de productos (GET, POST)
  - Salida con colores para mejor visualización
  - Verificación de todos los criterios de aceptación

- **Documentación de Pruebas**: `PRUEBAS_PRODUCTOS.md`
  - Resultados de todas las pruebas
  - Ejemplos de requests y responses
  - Confirmación de cumplimiento de criterios

### 📚 Documentación

- **README.md**: Actualizado con:
  - Nueva sección de endpoints de productos
  - Ejemplos de uso con cURL para productos
  - Estructura de proyecto actualizada
  - Información sobre pruebas automatizadas

- **CHANGELOG.md**: Este archivo
  - Registro detallado de cambios

### 📦 Dependencias

- **Añadidas al requirements.txt**:
  - `requests==2.31.0`: Para script de pruebas
  - `colorama==0.4.6`: Para salida con colores en pruebas

### ✅ Criterios de Aceptación Cumplidos

#### Autenticación
- ✅ Enviar credenciales válidas al endpoint `/auth/login` devuelve un JWT válido
- ✅ Enviar credenciales inválidas devuelve 401 Unauthorized

#### Gestión de Productos
- ✅ GET `/products` devuelve un listado en JSON que incluye al menos id, name y price
- ✅ POST `/products` crea un nuevo producto en la base de datos y responde con 201 Created

### 🔧 Mejoras Técnicas

- Manejo robusto de errores con try-catch en endpoints
- Validaciones automáticas con Pydantic
- Transacciones de base de datos con rollback en caso de error
- Timestamps automáticos (created_at, updated_at)
- UUIDs para identificadores únicos

---

## [1.0.0] - 2025-10-09

### Funcionalidades Iniciales

- Sistema de autenticación JWT completo
- Endpoints de registro, login, logout
- Refresh tokens
- Verificación de tokens
- Hash de contraseñas con bcrypt
- Base de datos SQLite con SQLAlchemy
- Documentación automática con Swagger UI

