# Pruebas de Endpoints - Autenticación y Productos

## Resumen de Implementación

Se implementaron exitosamente los siguientes componentes:

1. **Modelo de Producto** (`app/models.py`)
   - Tabla `products` con campos: id, name, description, price, stock, is_active, created_at, updated_at

2. **Esquemas Pydantic** (`app/schemas.py`)
   - `ProductBase`, `ProductCreate`, `ProductUpdate`, `ProductResponse`

3. **Endpoints de Productos** (`app/routes.py`)
   - `GET /api/v1/products` - Listar productos
   - `POST /api/v1/products` - Crear producto

---

## Pruebas Realizadas

### ✅ 1. Autenticación - Login con Credenciales Válidas

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'
```

**Response: 200 OK**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**✓ Criterio cumplido:** Enviar credenciales válidas al endpoint `/auth/login` devuelve un JWT válido.

---

### ✅ 2. Autenticación - Login con Credenciales Inválidas

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"wrongpassword"}'
```

**Response: 401 Unauthorized**
```json
{
  "detail": "Credenciales incorrectas"
}
```

**✓ Criterio cumplido:** Enviar credenciales inválidas devuelve 401 Unauthorized.

---

### ✅ 3. Productos - GET /products (Listado Vacío)

**Request:**
```bash
curl -X GET http://localhost:8000/api/v1/products \
  -H "Content-Type: application/json"
```

**Response: 200 OK**
```json
[]
```

**✓ Criterio cumplido:** GET `/products` devuelve un listado en JSON (inicialmente vacío).

---

### ✅ 4. Productos - POST /products (Crear Producto)

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptop",
    "description": "Laptop HP 15 pulgadas",
    "price": 899.99,
    "stock": 10
  }'
```

**Response: 201 Created**
```json
{
  "id": "23716cc5-1b5e-4f47-8012-3d81e31448fe",
  "name": "Laptop",
  "description": "Laptop HP 15 pulgadas",
  "price": 899.99,
  "stock": 10,
  "is_active": true,
  "created_at": "2025-10-10T03:50:03.405408",
  "updated_at": "2025-10-10T03:50:03.405411"
}
```

**✓ Criterio cumplido:** POST `/products` crea un nuevo producto en la base de datos y responde con 201 Created.

---

### ✅ 5. Productos - GET /products (Listado con Productos)

**Request:**
```bash
curl -X GET http://localhost:8000/api/v1/products \
  -H "Content-Type: application/json"
```

**Response: 200 OK**
```json
[
  {
    "id": "23716cc5-1b5e-4f47-8012-3d81e31448fe",
    "name": "Laptop",
    "description": "Laptop HP 15 pulgadas",
    "price": 899.99,
    "stock": 10,
    "is_active": true,
    "created_at": "2025-10-10T03:50:03.405408",
    "updated_at": "2025-10-10T03:50:03.405411"
  },
  {
    "id": "5c6de45b-ab60-4c5f-857c-c92b71e7e0a8",
    "name": "Mouse Inalámbrico",
    "description": "Mouse Logitech MX Master",
    "price": 79.99,
    "stock": 25,
    "is_active": true,
    "created_at": "2025-10-10T03:50:16.433166",
    "updated_at": "2025-10-10T03:50:16.433170"
  }
]
```

**✓ Criterio cumplido:** GET `/products` devuelve un listado en JSON que incluye al menos `id`, `name` y `price`.

---

## Conclusión

✅ **Todos los criterios de aceptación fueron cumplidos:**

1. ✅ Endpoint `/auth/login` devuelve JWT válido con credenciales correctas
2. ✅ Endpoint `/auth/login` devuelve 401 Unauthorized con credenciales incorrectas
3. ✅ GET `/products` devuelve listado JSON con id, name y price
4. ✅ POST `/products` crea producto y responde con 201 Created

## Estructura del Proyecto

```
apiMS/
├── app/
│   ├── models.py          # Modelos User y Product
│   ├── schemas.py         # Esquemas Pydantic para validación
│   ├── routes.py          # Endpoints de auth y products
│   ├── auth_service.py    # Servicio de autenticación
│   ├── database.py        # Configuración de SQLAlchemy
│   ├── main.py           # Aplicación FastAPI
│   └── config.py         # Configuración
├── auth_api.db           # Base de datos SQLite
└── PRUEBAS_PRODUCTOS.md  # Este documento
```

## Cómo Ejecutar

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Iniciar el servidor:
   ```bash
   python run.py
   ```

3. Acceder a la documentación interactiva:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Ejemplos de Uso con Python

### Registrar Usuario
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/auth/register",
    json={
        "email": "usuario@example.com",
        "username": "usuario",
        "password": "password123",
        "full_name": "Usuario de Prueba"
    }
)
print(response.json())
```

### Login
```python
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={
        "username": "usuario",
        "password": "password123"
    }
)
tokens = response.json()
access_token = tokens["access_token"]
```

### Crear Producto
```python
response = requests.post(
    "http://localhost:8000/api/v1/products",
    json={
        "name": "Teclado Mecánico",
        "description": "Teclado mecánico RGB",
        "price": 129.99,
        "stock": 15
    }
)
print(response.json())
```

### Listar Productos
```python
response = requests.get("http://localhost:8000/api/v1/products")
productos = response.json()
for producto in productos:
    print(f"{producto['name']}: ${producto['price']}")
```

