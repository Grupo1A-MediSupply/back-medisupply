# 📚 Índice de Documentación

Bienvenido al sistema de microservicios con arquitectura hexagonal. Esta guía te ayudará a navegar por toda la documentación.

## 🎯 Empieza Aquí

Si eres nuevo en el proyecto, sigue este orden:

1. **[QUICKSTART.md](QUICKSTART.md)** ⚡
   - Poner en marcha el proyecto en 5 minutos
   - Pruebas rápidas
   - Solución de problemas comunes

2. **[README.md](README.md)** 📖
   - Visión general del proyecto
   - Estructura de microservicios
   - Ejemplos de uso
   - Guía completa

3. **[ARCHITECTURE.md](ARCHITECTURE.md)** 🏗️
   - Arquitectura hexagonal explicada
   - CQRS y Event-Driven Architecture
   - Patrones de diseño
   - Diagramas detallados

4. **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** ✅
   - Resumen de lo implementado
   - Lista de componentes
   - Métricas del proyecto
   - Próximos pasos

## 📂 Estructura de Carpetas

```
microservices/
├── 📄 INDEX.md                    ← Estás aquí
├── 📄 README.md                   ← Documentación principal
├── 📄 QUICKSTART.md               ← Inicio rápido
├── 📄 ARCHITECTURE.md             ← Arquitectura detallada
├── 📄 IMPLEMENTATION_SUMMARY.md   ← Resumen de implementación
├── 📄 requirements.txt            ← Dependencias Python
├── 📄 docker-compose.yml          ← Orquestación Docker
│
├── 📁 shared/                     ← Código compartido
│   └── domain/
│       ├── entity.py             ← Entidad base
│       ├── events.py             ← Event bus
│       └── value_objects.py      ← Value objects
│
├── 📁 auth-service/               ← Microservicio de autenticación
│   ├── domain/                   ← Lógica de negocio
│   ├── application/              ← Casos de uso (CQRS)
│   ├── infrastructure/           ← Adaptadores
│   ├── api/                      ← REST API
│   ├── main.py                   ← Aplicación
│   ├── run.py                    ← Script de ejecución
│   └── Dockerfile                ← Imagen Docker
│
└── 📁 product-service/            ← Microservicio de productos
    ├── domain/                   ← Lógica de negocio
    ├── application/              ← Casos de uso (CQRS)
    ├── infrastructure/           ← Adaptadores
    ├── api/                      ← REST API
    ├── main.py                   ← Aplicación
    ├── run.py                    ← Script de ejecución
    └── Dockerfile                ← Imagen Docker
```

## 🗺️ Navegación por Temas

### 🚀 Empezando
- [Instalación y Setup](QUICKSTART.md#instalación-local)
- [Ejecutar con Docker](QUICKSTART.md#opción-2-ejecución-con-docker)
- [Primeras Pruebas](QUICKSTART.md#-pruebas-rápidas)

### 🏗️ Arquitectura
- [Arquitectura Hexagonal](ARCHITECTURE.md#arquitectura-hexagonal)
- [CQRS Pattern](ARCHITECTURE.md#2-cqrs-command-query-responsibility-segregation)
- [Event-Driven](ARCHITECTURE.md#3-event-driven-architecture)
- [Domain-Driven Design](ARCHITECTURE.md#4-domain-driven-design-ddd)

### 📦 Microservicios
- [Auth Service](README.md#1-auth-service-puerto-8001)
- [Product Service](README.md#2-product-service-puerto-8002)
- [Comunicación entre servicios](ARCHITECTURE.md#event-driven-architecture)

### 💻 Código
- [Estructura del Dominio](ARCHITECTURE.md#capa-de-dominio-domain-layer)
- [Comandos y Queries](ARCHITECTURE.md#cqrs-en-acción)
- [Eventos](ARCHITECTURE.md#-eventos-de-dominio)
- [Repositorios](ARCHITECTURE.md#puertos-y-adaptadores)

### 🧪 Testing
- [Estrategia de Testing](ARCHITECTURE.md#-testing-strategy)
- [Unit Tests](ARCHITECTURE.md#unit-tests-dominio)
- [Integration Tests](ARCHITECTURE.md#integration-tests-aplicación--infraestructura)
- [E2E Tests](ARCHITECTURE.md#e2e-tests-api-completa)

### 🐳 Docker
- [Dockerfile Auth Service](auth-service/Dockerfile)
- [Dockerfile Product Service](product-service/Dockerfile)
- [Docker Compose](docker-compose.yml)

### 🔐 Seguridad
- [Autenticación JWT](README.md#-seguridad)
- [Manejo de Tokens](ARCHITECTURE.md#autenticación)
- [Validación](ARCHITECTURE.md#validación)

## 🎓 Guías por Nivel

### 👶 Principiante
1. Lee el [QUICKSTART.md](QUICKSTART.md)
2. Ejecuta el proyecto localmente
3. Prueba los endpoints en Swagger UI
4. Observa los logs de eventos en la consola

### 👨‍💻 Intermedio
1. Lee [README.md](README.md) completo
2. Explora el código del dominio
3. Entiende los comandos y queries
4. Modifica un endpoint existente

### 🧙 Avanzado
1. Lee [ARCHITECTURE.md](ARCHITECTURE.md)
2. Implementa un nuevo microservicio
3. Agrega un nuevo patrón
4. Integra un message broker

## 📖 Documentación por Microservicio

### Auth Service (Puerto 8001)

**Documentación:**
- [Endpoints](README.md#1-auth-service-puerto-8001)
- [Dominio](ARCHITECTURE.md#domain-driven-design-ddd)
- [Comandos](auth-service/application/commands/)
- [Queries](auth-service/application/queries/)

**Archivos clave:**
```
auth-service/
├── domain/entities/User.py           ← Entidad User
├── application/handlers/             ← Command/Query handlers
├── infrastructure/repositories/      ← Repositorio de usuarios
└── api/routes/                       ← Endpoints REST
```

### Product Service (Puerto 8002)

**Documentación:**
- [Endpoints](README.md#2-product-service-puerto-8002)
- [Dominio](ARCHITECTURE.md#domain-driven-design-ddd)
- [Comandos](product-service/application/commands/)
- [Queries](product-service/application/queries/)

**Archivos clave:**
```
product-service/
├── domain/entities/Product.py        ← Entidad Product
├── application/handlers/             ← Command/Query handlers
├── infrastructure/repositories/      ← Repositorio de productos
└── api/routes/                       ← Endpoints REST
```

## 🔍 Buscar por Concepto

### Arquitectura Hexagonal
- [¿Qué es?](ARCHITECTURE.md#1-arquitectura-hexagonal-ports--adapters)
- [Capas](ARCHITECTURE.md#estructura-de-capas)
- [Puertos](ARCHITECTURE.md#puertos-interfaces)
- [Adaptadores](ARCHITECTURE.md#adaptadores-implementaciones)

### CQRS
- [¿Qué es?](ARCHITECTURE.md#2-cqrs-command-query-responsibility-segregation)
- [Comandos](ARCHITECTURE.md#comandos-escritura)
- [Queries](ARCHITECTURE.md#queries-lectura)
- [Handlers](README.md#-cqrs-en-acción)

### Event-Driven
- [¿Qué es?](ARCHITECTURE.md#3-event-driven-architecture)
- [Eventos de Dominio](ARCHITECTURE.md#eventos-de-dominio)
- [Event Bus](ARCHITECTURE.md#event-bus)
- [Event Handlers](ARCHITECTURE.md#event-handlers)

### DDD
- [Entidades](ARCHITECTURE.md#entidades)
- [Value Objects](ARCHITECTURE.md#value-objects)
- [Agregados](ARCHITECTURE.md#agregados)

## 🛠️ Recursos Útiles

### APIs
- **Auth Service Swagger:** http://localhost:8001/docs
- **Product Service Swagger:** http://localhost:8002/docs
- **Auth Health Check:** http://localhost:8001/health
- **Product Health Check:** http://localhost:8002/health

### Comandos Útiles

```bash
# Ejecutar servicios localmente
cd auth-service && python run.py
cd product-service && python run.py

# Ejecutar con Docker
docker-compose up --build

# Ver logs
docker-compose logs -f auth-service
docker-compose logs -f product-service

# Detener servicios
docker-compose down

# Reinstalar dependencias
pip install -r requirements.txt
```

### Scripts de Prueba

Consulta [QUICKSTART.md](QUICKSTART.md#-pruebas-rápidas) para:
- Registrar usuarios
- Hacer login
- Crear productos
- Gestionar inventario

## 📊 Diagramas

### Arquitectura General
Ver en [README.md](README.md#-diagramas)

### Flujos de Datos
Ver en [ARCHITECTURE.md](ARCHITECTURE.md#-flujos-de-datos)

### Capas
Ver en [ARCHITECTURE.md](ARCHITECTURE.md#-estructura-de-capas)

## 🎯 Casos de Uso Comunes

### "Quiero agregar un nuevo endpoint"
1. Define el comando/query en `application/commands/` o `application/queries/`
2. Crea el handler en `application/handlers/`
3. Registra la dependencia en `api/dependencies/`
4. Crea la ruta en `api/routes/`

### "Quiero agregar un nuevo microservicio"
1. Copia la estructura de auth-service o product-service
2. Define tu dominio (entidades, VOs, eventos)
3. Implementa comandos y queries
4. Crea los handlers
5. Implementa repositorios
6. Crea la API REST
7. Agrega al docker-compose.yml

### "Quiero entender cómo funciona X"
1. Busca en este índice
2. Lee la documentación específica
3. Revisa el código fuente
4. Prueba modificar y observa los cambios

## 🆘 Ayuda

### ¿Problema al ejecutar?
→ [QUICKSTART.md - Solución de Problemas](QUICKSTART.md#-solución-de-problemas)

### ¿No entiendes la arquitectura?
→ [ARCHITECTURE.md](ARCHITECTURE.md)

### ¿Quieres ver ejemplos?
→ [README.md - Ejemplos](README.md#-ejemplos-de-uso)

### ¿Necesitas referencia de API?
→ http://localhost:8001/docs (Auth)  
→ http://localhost:8002/docs (Products)

## 📚 Referencias Externas

- [Clean Architecture - Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Hexagonal Architecture - Alistair Cockburn](https://alistair.cockburn.us/hexagonal-architecture/)
- [CQRS Pattern - Martin Fowler](https://martinfowler.com/bliki/CQRS.html)
- [Domain-Driven Design](https://www.domainlanguage.com/ddd/)
- [Event-Driven Architecture](https://martinfowler.com/articles/201701-event-driven.html)

## 🗂️ Tabla de Contenidos Completa

### Documentación
- ✅ INDEX.md (este archivo)
- ✅ README.md
- ✅ QUICKSTART.md
- ✅ ARCHITECTURE.md
- ✅ IMPLEMENTATION_SUMMARY.md

### Configuración
- ✅ requirements.txt
- ✅ docker-compose.yml
- ✅ .env.example

### Microservicios
- ✅ Auth Service (completo)
- ✅ Product Service (completo)

### Módulo Compartido
- ✅ Entity base
- ✅ Event bus
- ✅ Value objects

## 🎉 ¡Listo para Empezar!

**Recomendación:** Comienza por el [QUICKSTART.md](QUICKSTART.md) y luego explora según tu nivel de experiencia.

---

**Última actualización:** 2025-01-10  
**Versión:** 1.0.0

¡Happy Coding! 🚀

