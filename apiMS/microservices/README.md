# Microservicios con Arquitectura Hexagonal

Sistema de microservicios implementado con **Arquitectura Hexagonal** (Ports & Adapters), **CQRS**, **Event-Driven Architecture** y **Domain-Driven Design (DDD)**.

## 🏗️ Arquitectura

### Patrones Implementados

1. **Arquitectura Hexagonal (Ports & Adapters)**
   - Separación clara entre dominio, aplicación e infraestructura
   - Puertos (interfaces) para la comunicación entre capas
   - Adaptadores para implementaciones específicas

2. **CQRS (Command Query Responsibility Segregation)**
   - Comandos para operaciones de escritura
   - Queries para operaciones de lectura
   - Handlers separados para cada operación

3. **Event-Driven Architecture**
   - Eventos de dominio
   - Event bus para publicación/suscripción
   - Event handlers para reaccionar a eventos

4. **Domain-Driven Design (DDD)**
   - Entidades con lógica de negocio
   - Value Objects inmutables
   - Agregados y raíces de agregado

## 📦 Microservicios

### 1. Auth Service (Puerto 8001)

Microservicio de autenticación y gestión de usuarios.

**Responsabilidades:**
- Registro de usuarios con validación de email y username
- Autenticación con verificación por código de email
- Gestión de tokens JWT (access & refresh)
- Verificación de tokens y códigos de autenticación
- Gestión de perfiles de usuario (nombre, teléfono)
- Cambio de contraseñas
- Activación/desactivación de usuarios

**Endpoints principales:**
- `POST /api/v1/auth/register` - Registrar usuario
- `POST /api/v1/auth/login` - Iniciar sesión (envía código por email)
- `POST /api/v1/auth/verify-code` - Verificar código de autenticación
- `POST /api/v1/auth/refresh` - Refrescar token
- `GET /api/v1/auth/me` - Obtener perfil actual
- `GET /api/v1/auth/verify` - Verificar token
- `PUT /api/v1/auth/profile` - Actualizar perfil
- `PUT /api/v1/auth/change-password` - Cambiar contraseña

### 2. Product Service (Puerto 8002)

Microservicio de gestión de productos e inventario.

**Responsabilidades:**
- Creación y actualización de productos
- Gestión de inventario (stock)
- Consulta de productos
- Activación/desactivación de productos

**Endpoints principales:**
- `POST /api/v1/products` - Crear producto
- `GET /api/v1/products` - Listar productos
- `GET /api/v1/products/{id}` - Obtener producto
- `PUT /api/v1/products/{id}` - Actualizar producto
- `POST /api/v1/products/{id}/stock/add` - Agregar stock
- `POST /api/v1/products/{id}/stock/remove` - Remover stock

## 📁 Estructura del Proyecto

```
microservices/
├── shared/                          # Módulo compartido
│   └── domain/
│       ├── entity.py               # Entidad base
│       ├── events.py               # Event bus y eventos base
│       └── value_objects.py        # Value objects compartidos
│
├── auth-service/                    # Microservicio de autenticación
│   ├── domain/                     # Capa de dominio
│   │   ├── entities/               # Entidades (User)
│   │   ├── value_objects/          # Value objects (Username, Password, PhoneNumber)
│   │   ├── events/                 # Eventos de dominio (UserRegistered, UserLoggedIn)
│   │   └── ports/                  # Puertos (interfaces)
│   │
│   ├── application/                # Capa de aplicación
│   │   ├── commands/               # Comandos (RegisterUser, Login, VerifyCode)
│   │   ├── queries/                # Queries (GetUser, VerifyToken, GetCurrentUser)
│   │   ├── handlers/               # Handlers para comandos/queries
│   │   └── services/               # Event handlers
│   │
│   ├── infrastructure/             # Capa de infraestructura
│   │   ├── adapters/               # Adaptadores (JWT, Password Hasher)
│   │   ├── repositories/           # Repositorios (SQLAlchemy)
│   │   ├── email_service.py        # Servicio de email
│   │   ├── verification_code_repository.py  # Repositorio de códigos
│   │   ├── config.py               # Configuración
│   │   └── database.py             # Setup de base de datos
│   │
│   ├── api/                        # Capa de API REST
│   │   ├── routes/                 # Rutas de FastAPI
│   │   └── dependencies/           # Inyección de dependencias
│   │
│   ├── tests/                      # Tests unitarios
│   │   ├── unit/                   # Tests unitarios
│   │   │   ├── test_entities.py    # Tests de entidades
│   │   │   ├── test_value_objects.py # Tests de value objects
│   │   │   ├── test_command_handlers.py # Tests de command handlers
│   │   │   ├── test_query_handlers.py # Tests de query handlers
│   │   │   └── test_domain_events.py # Tests de eventos de dominio
│   │   └── conftest.py             # Fixtures de pytest
│   │
│   ├── main.py                     # Aplicación principal
│   ├── run.py                      # Script de ejecución
│   └── Dockerfile                  # Imagen Docker
│
├── product-service/                # Microservicio de productos
│   ├── domain/                     # (misma estructura que auth-service)
│   ├── application/
│   ├── infrastructure/
│   ├── api/
│   ├── main.py
│   ├── run.py
│   └── Dockerfile
│
├── docker-compose.yml              # Orquestación de servicios
├── requirements.txt                # Dependencias Python
└── README.md                       # Este archivo
```

## 🚀 Inicio Rápido

### Requisitos Previos

- Python 3.11+
- Docker y Docker Compose (opcional)
- pip

### Instalación Local

1. **Clonar el repositorio**
```bash
cd /Users/lucasblandon/PROYECTOFINAL/codigoV5/apiMS/microservices
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Ejecutar Auth Service**
```bash
cd auth-service
python run.py
# Servicio disponible en http://localhost:8001
```

4. **Ejecutar Product Service** (en otra terminal)
```bash
cd product-service
python run.py
# Servicio disponible en http://localhost:8002
```

### Ejecución con Docker Compose

1. **Construir y ejecutar todos los servicios**
```bash
docker-compose up --build
```

2. **Acceder a los servicios**
- Auth Service: http://localhost:8001/docs
- Product Service: http://localhost:8002/docs

3. **Detener los servicios**
```bash
docker-compose down
```

## 📚 Documentación de la Arquitectura

### Capa de Dominio (Domain Layer)

**Responsabilidad:** Contiene la lógica de negocio pura, sin dependencias externas.

- **Entidades:** Objetos con identidad única que encapsulan reglas de negocio
- **Value Objects:** Objetos inmutables sin identidad
- **Eventos de Dominio:** Representan hechos que ocurrieron en el dominio
- **Puertos:** Interfaces que definen contratos

**Ejemplo:**
```python
class User(Entity):
    """Entidad User con lógica de negocio"""
    
    def login(self):
        """Registrar evento de login"""
        if not self._is_active:
            raise ValueError("Usuario desactivado")
        
        self._record_event(UserLoggedInEvent(
            user_id=str(self._id),
            username=str(self._username)
        ))
```

### Capa de Aplicación (Application Layer)

**Responsabilidad:** Orquesta el flujo de la aplicación usando el dominio.

- **Comandos:** Representan intenciones de cambio (escritura)
- **Queries:** Representan intenciones de lectura
- **Handlers:** Procesan comandos y queries
- **Event Handlers:** Reaccionan a eventos de dominio

**Ejemplo:**
```python
class RegisterUserCommandHandler:
    """Handler para registrar usuario"""
    
    async def handle(self, command: RegisterUserCommand) -> User:
        # 1. Validar
        # 2. Crear entidad
        user = User.register(...)
        
        # 3. Guardar
        user = await self.user_repository.save(user)
        
        # 4. Publicar eventos
        for event in user.get_domain_events():
            await event_bus.publish(event)
        
        return user
```

### Capa de Infraestructura (Infrastructure Layer)

**Responsabilidad:** Implementaciones concretas de las interfaces del dominio.

- **Adaptadores:** Implementaciones de puertos (JWT, BCrypt, etc.)
- **Repositorios:** Acceso a datos (SQLAlchemy, MongoDB, etc.)
- **Configuración:** Settings y variables de entorno
- **Base de datos:** Setup y conexiones

**Ejemplo:**
```python
class SQLAlchemyUserRepository(IUserRepository):
    """Implementación concreta del repositorio"""
    
    async def save(self, user: User) -> User:
        model = self._to_model(user)
        self.db.add(model)
        self.db.commit()
        return user
```

### Capa de API (API Layer)

**Responsabilidad:** Expone la funcionalidad a través de HTTP REST.

- **Rutas:** Endpoints de FastAPI
- **Schemas:** Modelos Pydantic para validación
- **Dependencies:** Inyección de dependencias

## 🎯 CQRS en Acción

### Comandos (Escritura)

```python
# Comando
@dataclass
class CreateProductCommand:
    name: str
    price: float
    stock: int

# Handler
class CreateProductCommandHandler:
    async def handle(self, command: CreateProductCommand):
        product = Product.create(...)
        product = await self.repository.save(product)
        await event_bus.publish(product.get_domain_events())
        return product

# Uso en API
@router.post("/products")
async def create_product(
    request: CreateProductRequest,
    handler=Depends(get_create_product_handler)
):
    command = CreateProductCommand(...)
    product = await handler.handle(command)
    return product
```

### Queries (Lectura)

```python
# Query
@dataclass
class GetProductByIdQuery:
    product_id: str

# Handler
class GetProductByIdQueryHandler:
    async def handle(self, query: GetProductByIdQuery):
        return await self.repository.find_by_id(query.product_id)

# Uso en API
@router.get("/products/{product_id}")
async def get_product(
    product_id: str,
    handler=Depends(get_product_by_id_handler)
):
    query = GetProductByIdQuery(product_id=product_id)
    product = await handler.handle(query)
    return product
```

## 🔔 Eventos de Dominio

### Definición de Eventos

```python
class ProductCreatedEvent(DomainEvent):
    def __init__(self, product_id: str, name: str, price: float):
        super().__init__()
        self.product_id = product_id
        self.name = name
        self.price = price
```

### Event Handlers

```python
class ProductEventHandler:
    async def on_product_created(self, event: ProductCreatedEvent):
        print(f"Producto creado: {event.name}")
        # Enviar notificación
        # Actualizar caché
        # Sincronizar con otros servicios
```

### Suscripción a Eventos

```python
def setup_event_handlers(event_handler: ProductEventHandler):
    event_bus.subscribe("ProductCreatedEvent", event_handler.on_product_created)
    event_bus.subscribe("LowStockEvent", event_handler.on_low_stock)
```

## 🔄 Flujo de una Petición

```
Cliente → API REST → Handler → Domain Entity → Repository → Database
                       ↓
                   Event Bus
                       ↓
                 Event Handlers
```

1. **Cliente** hace una petición HTTP
2. **API** valida y crea un comando/query
3. **Handler** procesa el comando/query
4. **Entidad de Dominio** aplica reglas de negocio
5. **Repositorio** persiste los cambios
6. **Eventos** son publicados al event bus
7. **Event Handlers** reaccionan a los eventos

## 🧪 Ejemplos de Uso

### Registro de Usuario

```bash
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "SecurePass123!",
    "confirm_password": "SecurePass123!",
    "full_name": "Test User",
    "phone_number": "+1234567890"
  }'
```

### Login (envía código por email)

```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePass123!"
  }'
```

### Verificar Código de Autenticación

```bash
curl -X POST http://localhost:8001/api/v1/auth/verify-code \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-uuid-here",
    "code": "123456"
  }'
```

### Actualizar Perfil

```bash
curl -X PUT http://localhost:8001/api/v1/auth/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "full_name": "Updated Name",
    "phone_number": "+0987654321"
  }'
```

### Cambiar Contraseña

```bash
curl -X PUT http://localhost:8001/api/v1/auth/change-password \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "old_password": "OldPass123!",
    "new_password": "NewPass123!"
  }'
```

### Crear Producto

```bash
curl -X POST http://localhost:8002/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptop HP",
    "description": "Laptop HP 15 pulgadas",
    "price": 899.99,
    "stock": 10
  }'
```

### Listar Productos

```bash
curl -X GET http://localhost:8002/api/v1/products
```

## 🧪 Testing

### Ejecutar Tests Unitarios

```bash
# Ejecutar todos los tests
cd auth-service
python -m pytest tests/ -v

# Ejecutar tests específicos
python -m pytest tests/unit/test_entities.py -v
python -m pytest tests/unit/test_command_handlers.py -v

# Ejecutar con coverage
python -m pytest tests/ --cov=domain --cov=application --cov-report=html
```

### Cobertura de Tests

Los tests unitarios cubren:

- **Entidades de Dominio:** User entity con todos sus métodos
- **Value Objects:** Username, Email, HashedPassword, FullName, PhoneNumber
- **Command Handlers:** RegisterUser, Login, RefreshToken, ChangePassword, etc.
- **Query Handlers:** GetUserById, GetUserByUsername, VerifyToken, etc.
- **Eventos de Dominio:** UserRegistered, UserLoggedIn, UserDeactivated, etc.

### Estructura de Tests

```
tests/
├── unit/
│   ├── test_entities.py           # Tests de entidades
│   ├── test_value_objects.py      # Tests de value objects
│   ├── test_command_handlers.py   # Tests de command handlers
│   ├── test_query_handlers.py     # Tests de query handlers
│   └── test_domain_events.py      # Tests de eventos de dominio
└── conftest.py                    # Fixtures compartidas
```

## 🔐 Seguridad

- **JWT Tokens:** Auth service genera tokens JWT para autenticación
- **Password Hashing:** Bcrypt para hashear contraseñas
- **Email Verification:** Códigos de verificación por email
- **CORS:** Configurado para permitir orígenes específicos
- **Validación:** Pydantic para validación de entrada

## 🌟 Ventajas de esta Arquitectura

### Arquitectura Hexagonal
✅ **Independencia de frameworks** - El dominio no depende de FastAPI  
✅ **Testeable** - Fácil testear el dominio sin infraestructura  
✅ **Flexible** - Fácil cambiar adaptadores (DB, API, etc.)  
✅ **Mantenible** - Separación clara de responsabilidades

### CQRS
✅ **Escalabilidad** - Escalar lecturas y escrituras independientemente  
✅ **Optimización** - Modelos optimizados para cada caso  
✅ **Claridad** - Intención clara de cada operación  
✅ **Auditoría** - Comandos como log de cambios

### Event-Driven
✅ **Desacoplamiento** - Servicios no dependen directamente entre sí  
✅ **Extensibilidad** - Fácil agregar nuevos listeners  
✅ **Asincronía** - Procesamiento asíncrono de eventos  
✅ **Trazabilidad** - Eventos como historial

### Microservicios
✅ **Independencia** - Cada servicio puede evolucionar independientemente  
✅ **Escalabilidad** - Escalar servicios individuales según necesidad  
✅ **Resiliencia** - Falla de un servicio no afecta a otros  
✅ **Tecnología** - Cada servicio puede usar tecnologías diferentes

## 📊 Diagramas

### Arquitectura Hexagonal

```
┌─────────────────────────────────────────────────────────┐
│                     API Layer (HTTP)                    │
│                  ┌──────────────────┐                   │
│                  │  FastAPI Routes  │                   │
│                  └────────┬─────────┘                   │
└──────────────────────────┼──────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────┐
│              Application Layer (Use Cases)              │
│     ┌─────────────┐              ┌─────────────┐       │
│     │  Commands   │              │   Queries   │       │
│     └──────┬──────┘              └──────┬──────┘       │
│            │                            │               │
│     ┌──────┴──────┐              ┌─────┴──────┐       │
│     │  Handlers   │              │  Handlers  │       │
│     └──────┬──────┘              └──────┬─────┘       │
└────────────┼─────────────────────────────┼─────────────┘
             │                             │
┌────────────┼─────────────────────────────┼─────────────┐
│            │     Domain Layer            │             │
│     ┌──────┴──────┐       ┌──────────────┴────┐       │
│     │  Entities   │       │   Value Objects   │       │
│     └──────┬──────┘       └───────────────────┘       │
│            │                                            │
│     ┌──────┴──────┐       ┌───────────────────┐       │
│     │   Events    │       │      Ports        │       │
│     └─────────────┘       └──────────┬────────┘       │
└───────────────────────────────────────┼────────────────┘
                                        │
┌───────────────────────────────────────┼────────────────┐
│           Infrastructure Layer        │                │
│     ┌─────────────┐           ┌──────┴────────┐       │
│     │  Adapters   │           │  Repositories │       │
│     │ (JWT, etc)  │           │  (SQLAlchemy) │       │
│     └─────────────┘           └───────────────┘       │
│                                                        │
│     ┌─────────────────────────────────────────┐      │
│     │            Database                     │      │
│     └─────────────────────────────────────────┘      │
└───────────────────────────────────────────────────────┘
```

### Flujo CQRS

```
Command Flow:
Client → POST /api/v1/products
         ↓
    CreateProductCommand
         ↓
    CommandHandler
         ↓
    Domain Entity (Product.create())
         ↓
    Repository.save()
         ↓
    Event: ProductCreated
         ↓
    EventHandlers

Query Flow:
Client → GET /api/v1/products
         ↓
    GetProductsQuery
         ↓
    QueryHandler
         ↓
    Repository.find_all()
         ↓
    Return Products
```

## 🛠️ Tecnologías Utilizadas

- **FastAPI** - Framework web moderno y rápido
- **Pydantic** - Validación de datos
- **SQLAlchemy** - ORM para base de datos
- **JWT** - Tokens de autenticación
- **Bcrypt** - Hash de contraseñas
- **Docker** - Containerización
- **Python 3.11** - Lenguaje de programación

## 📝 Notas de Implementación

- Los eventos se procesan de forma síncrona actualmente
- Para producción, considerar usar un message broker (RabbitMQ, Kafka)
- Implementar API Gateway para enrutamiento centralizado
- Agregar circuit breakers para resiliencia
- Implementar distributed tracing (Jaeger, Zipkin)
- Agregar métricas y monitoreo (Prometheus, Grafana)

## 🔮 Próximas Mejoras

- [ ] API Gateway con Kong o Traefik
- [ ] Message Broker (RabbitMQ/Kafka)
- [ ] Event Sourcing completo
- [ ] Read Models separados
- [ ] Service Discovery (Consul/Eureka)
- [ ] Distributed Tracing
- [ ] Métricas y Dashboards
- [ ] Tests automatizados (unit, integration)
- [ ] CI/CD Pipeline

## 📖 Referencias

- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [CQRS Pattern](https://martinfowler.com/bliki/CQRS.html)
- [Domain-Driven Design](https://www.domainlanguage.com/ddd/)
- [Event-Driven Architecture](https://martinfowler.com/articles/201701-event-driven.html)

---

**Autor:** Sistema de Microservicios v1.0  
**Licencia:** MIT

