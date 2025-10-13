# 🚀 Guía de Inicio Rápido

Esta guía te ayudará a poner en marcha los microservicios en menos de 5 minutos.

## Prerrequisitos

✅ Python 3.11 o superior  
✅ Docker y Docker Compose (opcional)  
✅ Git  
✅ Terminal/CMD

## Opción 1: Ejecución Local (Desarrollo)

### Paso 1: Instalar Dependencias

```bash
cd /Users/lucasblandon/PROYECTOFINAL/codigoV5/apiMS/microservices
pip install -r requirements.txt
```

### Paso 2: Ejecutar Auth Service

En una terminal:

```bash
cd auth-service
python run.py
```

El servicio estará disponible en: **http://localhost:8001**

### Paso 3: Ejecutar Product Service

En otra terminal:

```bash
cd product-service
python run.py
```

El servicio estará disponible en: **http://localhost:8002**

### Paso 4: Probar los Servicios

Abre tu navegador y visita:
- **Auth Service Docs:** http://localhost:8001/docs
- **Product Service Docs:** http://localhost:8002/docs

## Opción 2: Ejecución con Docker (Recomendado)

### Paso 1: Construir y Ejecutar

```bash
cd /Users/lucasblandon/PROYECTOFINAL/codigoV5/apiMS/microservices
docker-compose up --build
```

### Paso 2: Acceder a los Servicios

- **Auth Service:** http://localhost:8001/docs
- **Product Service:** http://localhost:8002/docs

### Detener los Servicios

```bash
docker-compose down
```

## 🧪 Pruebas Rápidas

### 1. Registrar un Usuario

```bash
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "username": "admin",
    "password": "Admin123!",
    "full_name": "Admin User"
  }'
```

**Respuesta esperada:**
```json
{
  "id": "uuid-here",
  "email": "admin@example.com",
  "username": "admin",
  "full_name": "Admin User",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### 2. Iniciar Sesión

```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "Admin123!"
  }'
```

**Respuesta esperada:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

**💡 Guarda el `access_token` para las siguientes peticiones!**

### 3. Crear un Producto

```bash
curl -X POST http://localhost:8002/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptop Dell XPS 15",
    "description": "Laptop de alto rendimiento",
    "price": 1299.99,
    "stock": 10
  }'
```

**Respuesta esperada:**
```json
{
  "id": "uuid-here",
  "name": "Laptop Dell XPS 15",
  "description": "Laptop de alto rendimiento",
  "price": 1299.99,
  "stock": 10,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### 4. Listar Productos

```bash
curl -X GET http://localhost:8002/api/v1/products
```

### 5. Obtener Perfil de Usuario (Autenticado)

```bash
curl -X GET http://localhost:8001/api/v1/auth/me \
  -H "Authorization: Bearer TU_ACCESS_TOKEN_AQUI"
```

## 📝 Usando la Interfaz Swagger

### Auth Service (http://localhost:8001/docs)

1. **Registrar usuario:**
   - Click en `POST /api/v1/auth/register`
   - Click en "Try it out"
   - Completa los datos
   - Click en "Execute"

2. **Login:**
   - Click en `POST /api/v1/auth/login`
   - Ingresa username y password
   - Copia el `access_token`

3. **Autorizar:**
   - Click en el botón "Authorize" (🔒)
   - Pega el token
   - Click en "Authorize"

Ahora todas las peticiones autenticadas funcionarán!

### Product Service (http://localhost:8002/docs)

1. **Crear producto:**
   - Click en `POST /api/v1/products`
   - Click en "Try it out"
   - Completa los datos
   - Click en "Execute"

2. **Listar productos:**
   - Click en `GET /api/v1/products`
   - Click en "Execute"

3. **Agregar stock:**
   - Click en `POST /api/v1/products/{product_id}/stock/add`
   - Ingresa el ID del producto
   - Ingresa la cantidad
   - Click en "Execute"

## 🔍 Verificar que Todo Funciona

### Health Checks

```bash
# Auth Service
curl http://localhost:8001/health

# Product Service
curl http://localhost:8002/health
```

Ambos deben responder con:
```json
{
  "status": "healthy",
  "service": "service-name",
  "environment": "development"
}
```

## 🐛 Solución de Problemas

### Error: "Port already in use"

```bash
# Encontrar el proceso usando el puerto
lsof -i :8001  # o :8002

# Matar el proceso
kill -9 PID
```

### Error: "ModuleNotFoundError"

```bash
# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

### Error: "Database locked"

```bash
# Eliminar archivos de base de datos
rm auth-service/auth_service.db
rm product-service/product_service.db

# Reiniciar servicios
```

### Los contenedores no inician

```bash
# Ver logs
docker-compose logs auth-service
docker-compose logs product-service

# Reconstruir sin caché
docker-compose build --no-cache
docker-compose up
```

## 📊 Datos de Prueba

### Script para Poblar Base de Datos

Crea un archivo `seed_data.py`:

```python
import requests

BASE_URL_AUTH = "http://localhost:8001/api/v1"
BASE_URL_PRODUCT = "http://localhost:8002/api/v1"

# Registrar usuarios
users = [
    {"email": "admin@test.com", "username": "admin", "password": "Admin123!"},
    {"email": "user@test.com", "username": "user", "password": "User123!"}
]

for user in users:
    response = requests.post(f"{BASE_URL_AUTH}/auth/register", json=user)
    print(f"Usuario creado: {response.json()}")

# Crear productos
products = [
    {"name": "Laptop HP", "price": 899.99, "stock": 15},
    {"name": "Mouse Logitech", "price": 29.99, "stock": 50},
    {"name": "Teclado Mecánico", "price": 79.99, "stock": 30}
]

for product in products:
    response = requests.post(f"{BASE_URL_PRODUCT}/products", json=product)
    print(f"Producto creado: {response.json()}")
```

Ejecutar:
```bash
python seed_data.py
```

## 🎯 Siguientes Pasos

1. ✅ Explora la documentación completa en `README.md`
2. ✅ Revisa la arquitectura en `ARCHITECTURE.md`
3. ✅ Prueba todos los endpoints en Swagger UI
4. ✅ Modifica el código y observa los eventos en la consola
5. ✅ Agrega tus propias funcionalidades

## 💡 Tips

- **Hot Reload:** Los cambios en el código se recargan automáticamente
- **Logs:** Observa la consola para ver eventos de dominio
- **Debug:** Usa `DEBUG=true` en variables de entorno
- **Postman:** Importa los endpoints desde Swagger (OpenAPI spec)

## 🆘 Ayuda

Si encuentras problemas:

1. Revisa los logs en la consola
2. Verifica que los puertos no estén en uso
3. Asegúrate de tener las dependencias instaladas
4. Consulta la documentación completa

## 🎉 ¡Listo!

Ya tienes un sistema de microservicios con arquitectura hexagonal funcionando.

**Recursos útiles:**
- 📚 README completo: `README.md`
- 🏗️ Documentación de arquitectura: `ARCHITECTURE.md`
- 📖 API Docs: http://localhost:8001/docs y http://localhost:8002/docs

---

**¡Happy Coding! 🚀**

