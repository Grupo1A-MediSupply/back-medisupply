# 🏗️ Sistema de Microservicios con Arquitectura Hexagonal

Sistema de microservicios implementado con **Arquitectura Hexagonal**, **CQRS**, **Event-Driven Architecture** y **Domain-Driven Design (DDD)**.

## 📦 Contenido

Este proyecto implementa un sistema completo de microservicios utilizando las mejores prácticas de arquitectura de software:

- ✅ **Arquitectura Hexagonal** (Ports & Adapters)
- ✅ **CQRS** (Command Query Responsibility Segregation)
- ✅ **Event-Driven Architecture**
- ✅ **Domain-Driven Design (DDD)**
- ✅ **Microservicios independientes**
- ✅ **Docker y Docker Compose**

## 🚀 Inicio Rápido

### Estructura del Proyecto

```
apiMS/
├── microservices/              # Sistema de microservicios
│   ├── shared/                 # Código compartido
│   ├── auth-service/           # Servicio de autenticación
│   ├── product-service/        # Servicio de productos
│   ├── docker-compose.yml      # Orquestación
│   ├── requirements.txt        # Dependencias
│   ├── README.md              # Documentación completa
│   ├── QUICKSTART.md          # Guía rápida
│   ├── ARCHITECTURE.md        # Arquitectura detallada
│   └── INDEX.md               # Índice de documentación
└── .gitignore
```

## 📚 Documentación

Toda la documentación está en la carpeta `microservices/`:

- **[INDEX.md](microservices/INDEX.md)** - Índice navegable de toda la documentación
- **[README.md](microservices/README.md)** - Documentación principal completa
- **[QUICKSTART.md](microservices/QUICKSTART.md)** - Guía de inicio rápido (5 minutos)
- **[ARCHITECTURE.md](microservices/ARCHITECTURE.md)** - Arquitectura detallada con diagramas
- **[IMPLEMENTATION_SUMMARY.md](microservices/IMPLEMENTATION_SUMMARY.md)** - Resumen de implementación

## 🎯 Microservicios Implementados

### 1. Auth Service (Puerto 8001)
Microservicio de autenticación y gestión de usuarios con arquitectura hexagonal.

**Características:**
- Registro de usuarios
- Autenticación JWT
- Gestión de tokens (access + refresh)
- Verificación de tokens
- Gestión de perfiles

**Endpoints:**
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/auth/me`
- `GET /api/v1/auth/verify`

### 2. Product Service (Puerto 8002)
Microservicio de gestión de productos e inventario con arquitectura hexagonal.

**Características:**
- CRUD de productos
- Gestión de inventario
- Control de stock
- Alertas de stock bajo

**Endpoints:**
- `POST /api/v1/products`
- `GET /api/v1/products`
- `GET /api/v1/products/{id}`
- `PUT /api/v1/products/{id}`
- `POST /api/v1/products/{id}/stock/add`
- `POST /api/v1/products/{id}/stock/remove`

## 🚀 Ejecutar el Proyecto

### Opción 1: Ejecución Local

```bash
cd microservices

# Instalar dependencias
pip install -r requirements.txt

# Terminal 1: Auth Service
cd auth-service
python run.py
# → http://localhost:8001/docs

# Terminal 2: Product Service
cd product-service
python run.py
# → http://localhost:8002/docs
```

### Opción 2: Docker Compose (Recomendado)

```bash
cd microservices
docker-compose up --build
```

**Servicios disponibles:**
- Auth Service: http://localhost:8001/docs
- Product Service: http://localhost:8002/docs

## 🧪 Prueba Rápida

```bash
# 1. Registrar usuario
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "username": "admin",
    "password": "Admin123!",
    "full_name": "Admin User"
  }'

# 2. Login
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Admin123!"}'

# 3. Crear producto
curl -X POST http://localhost:8002/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptop Dell",
    "price": 1299.99,
    "stock": 10
  }'

# 4. Listar productos
curl http://localhost:8002/api/v1/products
```

## 🏗️ Arquitectura

### Arquitectura Hexagonal (Ports & Adapters)

Cada microservicio está organizado en capas:

```
┌─────────────────────────────────────┐
│         API Layer (HTTP)            │
│      FastAPI Routes & DTOs          │
└──────────────┬──────────────────────┘
               │
┌──────────────┴──────────────────────┐
│      Application Layer              │
│  Commands, Queries & Handlers       │
│         (CQRS)                      │
└──────────────┬──────────────────────┘
               │
┌──────────────┴──────────────────────┐
│        Domain Layer                 │
│  Entities, VOs, Events, Ports       │
│         (DDD)                       │
└──────────────↑──────────────────────┘
               │
┌──────────────┴──────────────────────┐
│     Infrastructure Layer            │
│  Adapters, Repositories, DB         │
└─────────────────────────────────────┘
```

### Patrones Implementados

1. **Hexagonal Architecture** - Desacoplamiento de capas
2. **CQRS** - Comandos y queries separados
3. **Event-Driven** - Comunicación por eventos
4. **Repository Pattern** - Abstracción de datos
5. **Factory Pattern** - Creación de entidades
6. **Dependency Injection** - Inyección de dependencias
7. **Value Object Pattern** - Objetos inmutables

## 📊 Estructura de Cada Microservicio

```
service/
├── domain/                    # Capa de Dominio
│   ├── entities/             # Entidades con lógica de negocio
│   ├── value_objects/        # Value Objects inmutables
│   ├── events/               # Eventos de dominio
│   └── ports/                # Interfaces (puertos)
│
├── application/              # Capa de Aplicación
│   ├── commands/             # Comandos (escritura)
│   ├── queries/              # Queries (lectura)
│   ├── handlers/             # Handlers para CQRS
│   └── services/             # Event handlers
│
├── infrastructure/           # Capa de Infraestructura
│   ├── adapters/             # Adaptadores (JWT, Bcrypt)
│   ├── repositories/         # Repositorios (SQLAlchemy)
│   ├── config.py            # Configuración
│   └── database.py          # Base de datos
│
├── api/                      # Capa de API
│   ├── routes/              # Endpoints REST
│   └── dependencies/        # Inyección de dependencias
│
├── main.py                  # Aplicación principal
├── run.py                   # Script de ejecución
└── Dockerfile               # Imagen Docker
```

## 🎯 Características Clave

### Arquitectura Hexagonal
- ✅ Dominio independiente de frameworks
- ✅ Puertos (interfaces) bien definidos
- ✅ Adaptadores intercambiables
- ✅ Testeable en todos los niveles

### CQRS
- ✅ Comandos para escritura
- ✅ Queries para lectura
- ✅ Handlers separados
- ✅ Escalabilidad independiente

### Event-Driven
- ✅ Eventos de dominio
- ✅ Event bus
- ✅ Event handlers
- ✅ Desacoplamiento de servicios

### DDD
- ✅ Entidades con lógica de negocio
- ✅ Value Objects inmutables
- ✅ Agregados
- ✅ Factory methods

## 🛠️ Tecnologías

- **Python 3.11** - Lenguaje de programación
- **FastAPI** - Framework web moderno
- **Pydantic** - Validación de datos
- **SQLAlchemy** - ORM para base de datos
- **JWT** - Autenticación
- **Bcrypt** - Hash de contraseñas
- **Docker** - Containerización
- **Docker Compose** - Orquestación

## 📖 Recursos

### Documentación del Proyecto
- [Índice de Documentación](microservices/INDEX.md)
- [Guía de Inicio Rápido](microservices/QUICKSTART.md)
- [Arquitectura Detallada](microservices/ARCHITECTURE.md)
- [Resumen de Implementación](microservices/IMPLEMENTATION_SUMMARY.md)

### APIs
- **Auth Service:** http://localhost:8001/docs
- **Product Service:** http://localhost:8002/docs
- **Health Checks:** `/health` en cada servicio

### Referencias Externas
- [Clean Architecture - Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Hexagonal Architecture - Alistair Cockburn](https://alistair.cockburn.us/hexagonal-architecture/)
- [CQRS Pattern - Martin Fowler](https://martinfowler.com/bliki/CQRS.html)
- [Domain-Driven Design](https://www.domainlanguage.com/ddd/)

## 🎓 Aprende Más

Si quieres entender mejor la arquitectura:

1. **Lee primero:** [QUICKSTART.md](microservices/QUICKSTART.md) - Para ejecutar el proyecto
2. **Luego:** [README.md completo](microservices/README.md) - Para entender la estructura
3. **Profundiza en:** [ARCHITECTURE.md](microservices/ARCHITECTURE.md) - Para dominar los conceptos

## 🆘 Solución de Problemas

**Puerto en uso:**
```bash
lsof -i :8001  # o :8002
kill -9 PID
```

**Reinstalar dependencias:**
```bash
cd microservices
pip install -r requirements.txt --force-reinstall
```

**Ver logs de Docker:**
```bash
cd microservices
docker-compose logs -f auth-service
docker-compose logs -f product-service
```

## 🌟 Ventajas de esta Arquitectura

✅ **Mantenible** - Código limpio y organizado  
✅ **Testeable** - Cada capa se prueba independientemente  
✅ **Escalable** - Servicios independientes  
✅ **Flexible** - Fácil cambiar implementaciones  
✅ **Extensible** - Agregar funcionalidades sin afectar lo existente  
✅ **Profesional** - Arquitectura de nivel empresarial  

## 📝 Licencia

MIT

---

**Versión:** 1.0.0  
**Fecha:** 2025-01-10  
**Estado:** ✅ Producción

Para más información, consulta la [documentación completa](microservices/README.md).

¡Happy Coding! 🚀

![Tests](https://github.com/USUARIO/REPO/actions/workflows/tests.yml/badge.svg)
![CI/CD](https://github.com/USUARIO/REPO/actions/workflows/ci-cd.yml/badge.svg)
![Coverage](https://codecov.io/gh/USUARIO/REPO/branch/main/graph/badge.svg)
![Python](https://img.shields.io/badge/python-3.11%20|%203.12-blue)
![Architecture](https://img.shields.io/badge/architecture-hexagonal-green)
![CQRS](https://img.shields.io/badge/pattern-CQRS-orange)
![Tests](https://img.shields.io/badge/tests-67%20passing-brightgreen)