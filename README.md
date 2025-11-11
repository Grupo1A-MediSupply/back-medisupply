# 🏥 MediSupply - Sistema de Microservicios

Sistema de gestión de suministros médicos implementado con **Arquitectura Hexagonal**, **CQRS**, **Event-Driven Architecture** y **Domain-Driven Design (DDD)**.

## 🚀 Ejecutar la Aplicación

### Requisitos Previos
- Docker Desktop instalado y ejecutándose
- Docker Compose v2.0+

### Opción 1: Docker Compose (Recomendado)

```bash
# 1. Construir y ejecutar todos los servicios
docker-compose up --build

# 2. Acceder a las APIs
# 🔐 Auth Service: http://localhost:8001/docs
# 📦 Product Service: http://localhost:8002/docs
```

### Opción 2: Docker Compose en Background

```bash
# Ejecutar en modo detached
docker-compose up -d --build

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down
```

### Opción 3: Desde el directorio de microservicios

```bash
# Navegar al directorio de microservicios
cd apiMS/microservices

# Ejecutar con Docker Compose
docker-compose up --build
```

## 📦 Microservicios

### 1. Auth Service (Puerto 8001)
- **URL:** http://localhost:8001/docs
- **Health Check:** http://localhost:8001/health
- **Funcionalidades:** 
  - Registro de usuarios con validación
  - Login con verificación por código de email
  - Gestión de tokens JWT (access & refresh)
  - Gestión de perfiles y cambio de contraseñas
  - Tests unitarios completos

### 2. Product Service (Puerto 8002)
- **URL:** http://localhost:8002/docs
- **Health Check:** http://localhost:8002/health
- **Funcionalidades:** CRUD de productos, gestión de inventario

## 🧪 Prueba Rápida

```bash
# 1. Registrar usuario
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","username":"admin","password":"Admin123!","confirm_password":"Admin123!","full_name":"Admin","phone_number":"+1234567890"}'

# 2. Login (envía código por email)
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin123!"}'

# 3. Verificar código (usar el código recibido por email)
curl -X POST http://localhost:8001/api/v1/auth/verify-code \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user-uuid-from-login-response","code":"123456"}'

# 4. Crear producto
curl -X POST http://localhost:8002/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Laptop","price":999.99,"stock":10}'

# 5. Ver productos
curl http://localhost:8002/api/v1/products
```

## 🔍 Troubleshooting

### Puerto Ocupado
```bash
# Windows
netstat -an | findstr :8001
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8001 | xargs kill -9
```

### Rebuild Completo
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Ver Logs
```bash
docker-compose logs -f auth-service
docker-compose logs -f product-service
```

## 🧪 Testing

### Ejecutar Tests Unitarios

```bash
# Ejecutar tests del Auth Service
cd apiMS/microservices/auth-service
python -m pytest tests/ -v

# Ejecutar con coverage
python -m pytest tests/ --cov=domain --cov=application --cov-report=html
```

### Cobertura de Tests

- ✅ **Entidades de Dominio:** User entity completa
- ✅ **Value Objects:** Username, Email, Password, PhoneNumber
- ✅ **Command Handlers:** Register, Login, ChangePassword, etc.
- ✅ **Query Handlers:** GetUser, VerifyToken, etc.
- ✅ **Eventos de Dominio:** UserRegistered, UserLoggedIn, etc.

## 📚 Documentación Completa

Para más detalles sobre la arquitectura y desarrollo local, consulta:
- [README.md](apiMS/microservices/README.md) - Documentación completa de microservicios
- [Tests Unitarios](apiMS/microservices/auth-service/tests/) - Tests del Auth Service

## 🛠️ Tecnologías

- **FastAPI** - Framework web
- **SQLAlchemy** - ORM
- **JWT** - Autenticación
- **Docker** - Containerización
- **Python 3.11** - Lenguaje

---

**¡Happy Coding! 🚀**
