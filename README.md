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
- **Funcionalidades:** Registro, login, gestión de tokens JWT

### 2. Product Service (Puerto 8002)
- **URL:** http://localhost:8002/docs
- **Health Check:** http://localhost:8002/health
- **Funcionalidades:** CRUD de productos, gestión de inventario

## 🧪 Prueba Rápida

```bash
# 1. Registrar usuario
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","username":"admin","password":"Admin123!","full_name":"Admin"}'

# 2. Login
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin123!"}'

# 3. Crear producto
curl -X POST http://localhost:8002/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Laptop","price":999.99,"stock":10}'

# 4. Ver productos
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

## 📚 Documentación Completa

Para más detalles sobre la arquitectura y desarrollo local, consulta:
- [START_HERE.md](apiMS/START_HERE.md) - Guía de inicio
- [README.md](apiMS/microservices/README.md) - Documentación de microservicios
- [ARCHITECTURE.md](apiMS/microservices/ARCHITECTURE.md) - Arquitectura detallada

## 🛠️ Tecnologías

- **FastAPI** - Framework web
- **SQLAlchemy** - ORM
- **JWT** - Autenticación
- **Docker** - Containerización
- **Python 3.11** - Lenguaje

---

**¡Happy Coding! 🚀**
