# MediSupply Monolith

Aplicación monolítica unificada que combina todos los microservicios de MediSupply en una sola aplicación FastAPI.

## 📋 Descripción

Este monolito migra todos los microservicios (Auth, Product, Order, Logistics, Inventory, Reports, Notifications) a una sola aplicación, conservando todos los endpoints y la arquitectura hexagonal original.

## 🏗️ Arquitectura

El monolito mantiene la estructura de cada servicio:
- **Domain Layer**: Entidades, Value Objects, Events, Ports
- **Application Layer**: Commands, Queries, Handlers, Services
- **Infrastructure Layer**: Repositories, Adapters, Database
- **API Layer**: Routes, Dependencies

### Estructura del Proyecto

```
medimn/
├── infrastructure/          # Configuración y base de datos unificada
│   ├── config.py            # Configuración unificada
│   └── database.py           # Base de datos unificada
├── shared/                   # Módulo compartido
│   ├── domain/              # Entidades y eventos base
│   └── infrastructure/       # Infraestructura compartida
├── auth/                     # Servicio de autenticación
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   └── api/
├── product/                  # Servicio de productos
├── order/                    # Servicio de órdenes
├── logistics/                # Servicio de logística
├── inventory/                # Servicio de inventario
├── reports/                  # Servicio de reportes
├── notifications/            # Servicio de notificaciones
├── main.py                   # Aplicación FastAPI unificada
├── requirements.txt          # Dependencias
└── Dockerfile               # Imagen Docker
```

## 🚀 Instalación

### Requisitos

- Python 3.11+
- PostgreSQL (opcional, SQLite por defecto)

### Instalación Local

```bash
# Clonar el repositorio
cd medimn

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno (opcional)
cp .env.example .env
# Editar .env con tus configuraciones

# Ejecutar la aplicación
python main.py
```

La aplicación estará disponible en `http://localhost:8000`

## 📚 Endpoints

Todos los endpoints de los microservicios están disponibles bajo `/api/v1/`:

### Auth Service
- `POST /api/v1/auth/register` - Registrar usuario
- `POST /api/v1/auth/login` - Iniciar sesión
- `POST /api/v1/auth/verify-code` - Verificar código
- `POST /api/v1/auth/refresh` - Refrescar token
- `GET /api/v1/auth/me` - Obtener perfil
- `GET /api/v1/auth/verify` - Verificar token
- `PUT /api/v1/auth/profile` - Actualizar perfil
- `PUT /api/v1/auth/change-password` - Cambiar contraseña

### Product Service
- `POST /api/v1/products` - Crear producto
- `GET /api/v1/products` - Listar productos
- `GET /api/v1/products/{id}` - Obtener producto
- `PUT /api/v1/products/{id}` - Actualizar producto
- `POST /api/v1/products/{id}/stock/add` - Agregar stock
- `POST /api/v1/products/{id}/stock/remove` - Remover stock

### Order Service
- `POST /api/v1/orders` - Crear orden
- `GET /api/v1/orders/{order_id}` - Obtener orden
- `PUT /api/v1/orders/{order_id}` - Actualizar orden
- `GET /api/v1/orders` - Listar órdenes
- `POST /api/v1/orders/{order_id}/confirm` - Confirmar orden
- `POST /api/v1/orders/{order_id}/cancel` - Cancelar orden

### Logistics Service
- `POST /api/v1/routes` - Crear ruta
- `GET /api/v1/routes/{route_id}` - Obtener ruta
- `POST /api/v1/routes/{route_id}/start` - Iniciar ruta
- `POST /api/v1/routes/{route_id}/complete` - Completar ruta
- `POST /api/v1/routes/{route_id}/cancel` - Cancelar ruta
- `GET /api/v1/routes` - Listar rutas

### Inventory Service
- `GET /api/v1/inventory` - Listar inventario
- `POST /api/v1/inventory/upload` - Subir inventario (CSV)

### Reports Service
- `GET /api/v1/reports` - Obtener reportes consolidados

### Notifications Service
- `GET /api/v1/notifications` - Listar notificaciones

## 🐳 Docker

### Construir imagen

```bash
docker build -t medisupply-monolith .
```

### Ejecutar contenedor

```bash
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e SECRET_KEY=your-secret-key \
  medisupply-monolith
```

### Docker Compose

```yaml
version: '3.8'
services:
  monolith:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/medisupply
      - SECRET_KEY=your-secret-key
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=medisupply
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## ⚙️ Configuración

Variables de entorno principales:

- `DATABASE_URL`: URL de conexión a la base de datos (default: `sqlite:///./medisupply.db`)
- `SECRET_KEY`: Clave secreta para JWT (requerido en producción)
- `SERVICE_PORT`: Puerto del servicio (default: `8000`)
- `ENVIRONMENT`: Entorno de ejecución (`development`, `production`)
- `DEBUG`: Modo debug (default: `True`)

Para configuración de email (Auth Service):
- `MAIL_USERNAME`: Usuario de email
- `MAIL_PASSWORD`: Contraseña de email
- `MAIL_FROM`: Email remitente
- `MAIL_SERVER`: Servidor SMTP
- `MAIL_PORT`: Puerto SMTP

## 📖 Documentación

La documentación interactiva de la API está disponible en:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔄 Migración desde Microservicios

Este monolito conserva:
- ✅ Todos los endpoints originales
- ✅ Misma estructura de respuestas
- ✅ Misma arquitectura hexagonal
- ✅ Mismos modelos de dominio
- ✅ Misma lógica de negocio

### Cambios principales:

1. **Base de datos unificada**: Todos los servicios comparten la misma base de datos
2. **Configuración centralizada**: Una sola configuración en `infrastructure/config.py`
3. **Imports adaptados**: Los servicios usan imports absolutos desde el monolito

## 🧪 Testing

```bash
# Ejecutar tests (si están disponibles)
pytest

# Con cobertura
pytest --cov=.
```

## 📝 Notas

- El monolito mantiene la separación de responsabilidades de cada servicio
- Los servicios pueden seguir evolucionando independientemente
- La migración de vuelta a microservicios es posible manteniendo la estructura

## 🤝 Contribución

Este monolito fue migrado desde los microservicios originales en `apiMS/microservices/`.

## 📄 Licencia

[Tu licencia aquí]

