# API de Autenticación y Gestión de Productos - FastAPI

Sistema de autenticación JWT y gestión de productos construido con FastAPI.

## Características

- **FastAPI** para la API REST
- **Pydantic** para validación de datos
- **SQLAlchemy** para ORM
- **JWT** para autenticación segura
- **Bcrypt** para hash de contraseñas
- **Gestión de productos** con endpoints CRUD
- Documentación automática con Swagger UI

## Instalación

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

## Configuración

Crear archivo `.env` basado en `.env.example`:

```bash
cp .env.example .env
```

Editar `.env` con tus configuraciones:
- `SECRET_KEY`: Clave secreta para JWT (generar una segura en producción)
- `DATABASE_URL`: URL de conexión a la base de datos
- Otros parámetros según necesites

## Ejecución

```bash
# Inicializar base de datos
python init_db.py

# Ejecutar servidor de desarrollo
python run.py

# O directamente con uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Endpoints de Autenticación

### POST /api/v1/auth/register
Registra un nuevo usuario en el sistema.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "full_name": "User Full Name"
}
```

### POST /api/v1/auth/login
Inicia sesión y obtiene tokens de acceso.

**Request Body:**
```json
{
  "username": "username",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### POST /api/v1/auth/refresh
Refresca el token de acceso usando el refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJ..."
}
```

### GET /api/v1/auth/me
Obtiene el perfil del usuario autenticado.

**Headers:**
```
Authorization: Bearer <access_token>
```

### POST /api/v1/auth/logout
Cierra la sesión del usuario.

**Headers:**
```
Authorization: Bearer <access_token>
```

### GET /api/v1/auth/verify
Verifica si un token es válido.

**Headers:**
```
Authorization: Bearer <access_token>
```

## Endpoints de Productos

### GET /api/v1/products
Obtiene el listado de todos los productos activos.

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Laptop",
    "description": "Laptop HP 15 pulgadas",
    "price": 899.99,
    "stock": 10,
    "is_active": true,
    "created_at": "2025-10-10T03:50:03.405408",
    "updated_at": "2025-10-10T03:50:03.405411"
  }
]
```

### POST /api/v1/products
Crea un nuevo producto en el sistema.

**Request Body:**
```json
{
  "name": "Laptop",
  "description": "Laptop HP 15 pulgadas",
  "price": 899.99,
  "stock": 10
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "name": "Laptop",
  "description": "Laptop HP 15 pulgadas",
  "price": 899.99,
  "stock": 10,
  "is_active": true,
  "created_at": "2025-10-10T03:50:03.405408",
  "updated_at": "2025-10-10T03:50:03.405411"
}
```

## Documentación API

Una vez ejecutado el servidor, la documentación estará disponible en:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Ejemplo de Uso con cURL

```bash
# 1. Registrar usuario
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "password123",
    "full_name": "Test User"
  }'

# 2. Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'

# 3. Obtener perfil (usar el access_token del login)
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer <access_token>"

# 4. Refrescar token
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<refresh_token>"
  }'

# 5. Verificar token
curl -X GET "http://localhost:8000/api/v1/auth/verify" \
  -H "Authorization: Bearer <access_token>"

# 6. Logout
curl -X POST "http://localhost:8000/api/v1/auth/logout" \
  -H "Authorization: Bearer <access_token>"
```

### Ejemplos de Productos

```bash
# 1. Listar productos
curl -X GET "http://localhost:8000/api/v1/products" \
  -H "Content-Type: application/json"

# 2. Crear producto
curl -X POST "http://localhost:8000/api/v1/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptop HP",
    "description": "Laptop HP 15 pulgadas",
    "price": 899.99,
    "stock": 10
  }'
```

## Estructura del Proyecto

```
apiMS/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicación principal
│   ├── config.py            # Configuración
│   ├── database.py          # Configuración de BD
│   ├── models.py            # Modelos SQLAlchemy (User, Product)
│   ├── schemas.py           # Esquemas Pydantic
│   ├── auth_service.py      # Lógica de autenticación
│   ├── jwt_service.py       # Manejo de JWT
│   └── routes.py            # Rutas de la API (auth + products)
├── .env                     # Variables de entorno (no versionado)
├── .env.example             # Ejemplo de variables
├── .gitignore
├── requirements.txt
├── README.md
├── init_db.py               # Script para inicializar BD
├── run.py                   # Script para ejecutar servidor
├── test_endpoints.py        # Script de pruebas automatizadas
├── PRUEBAS_PRODUCTOS.md     # Documentación de pruebas
└── EJEMPLOS_USO.md          # Ejemplos detallados
```

## Pruebas Automatizadas

El proyecto incluye un script de pruebas automatizadas que verifica todos los endpoints:

```bash
# Ejecutar pruebas (asegúrate de que el servidor esté corriendo)
python test_endpoints.py
```

Las pruebas verifican:
- ✅ Login con credenciales válidas devuelve JWT
- ✅ Login con credenciales inválidas devuelve 401 Unauthorized
- ✅ GET /products devuelve listado JSON con id, name y price
- ✅ POST /products crea producto y responde con 201 Created

Ver detalles en `PRUEBAS_PRODUCTOS.md`.

## Seguridad

- Las contraseñas se hashean con bcrypt
- Los tokens JWT tienen expiración configurable
- Access tokens: 30 minutos (configurable)
- Refresh tokens: 7 días
- Se valida el tipo de token (access/refresh)
- Protección contra tokens expirados

## Licencia

MIT

