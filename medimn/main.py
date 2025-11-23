"""
Aplicación monolítica unificada de MediSupply
Combina todos los microservicios en una sola aplicación FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
from pathlib import Path

# Agregar el directorio raíz al path para imports
root_path = Path(__file__).parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from infrastructure.config import get_settings
from infrastructure.database import create_tables, Base

# Importar todos los modelos para que se registren en Base.metadata
# Auth Service
try:
    from auth.infrastructure.repositories import UserModel, VerificationCodeModel
except ImportError:
    pass

# Product Service
try:
    from product.infrastructure.repositories import ProductModel
except ImportError:
    pass

# Order Service
try:
    from order.infrastructure.repositories.models import OrderModel
except ImportError:
    try:
        from order.infrastructure.repositories import OrderModel
    except ImportError:
        pass

# Logistics Service
try:
    from logistics.infrastructure.repositories import RouteModel
except ImportError:
    pass

# Inventory Service
try:
    from inventory.infrastructure.database import InventoryItemModel
except ImportError:
    pass

# Importar routers de todos los servicios
from auth.api.routes import router as auth_router
from product.api.routes import router as product_router
from order.api.routes import router as order_router
from logistics.api.routes import router as logistics_router
from inventory.api.routes import router as inventory_router
from reports.api.routes import router as reports_router
from notifications.api.routes import router as notifications_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    print(f"🚀 Iniciando {settings.service_name} en {settings.environment}")
    print(f"📦 Monolito unificado de MediSupply")
    print(f"   - Auth Service")
    print(f"   - Product Service")
    print(f"   - Order Service")
    print(f"   - Logistics Service")
    print(f"   - Inventory Service")
    print(f"   - Reports Service")
    print(f"   - Notifications Service")
    
    # Crear tablas de base de datos
    create_tables()
    print("✅ Base de datos inicializada")
    
    # Configurar event handlers de cada servicio
    try:
        from auth.application.services import UserEventHandler, setup_event_handlers as setup_auth_handlers
        event_handler = UserEventHandler()
        setup_auth_handlers(event_handler)
        print("✅ Auth event handlers configurados")
    except Exception as e:
        print(f"⚠️  Error configurando auth handlers: {e}")
    
    try:
        from product.application.services import ProductEventHandler, setup_event_handlers as setup_product_handlers
        event_handler = ProductEventHandler()
        setup_product_handlers(event_handler)
        print("✅ Product event handlers configurados")
    except Exception as e:
        print(f"⚠️  Error configurando product handlers: {e}")
    
    try:
        from order.application.services import OrderEventHandler, setup_event_handlers as setup_order_handlers
        event_handler = OrderEventHandler()
        setup_order_handlers(event_handler)
        print("✅ Order event handlers configurados")
    except Exception as e:
        print(f"⚠️  Error configurando order handlers: {e}")
    
    yield
    
    # Shutdown
    print(f"🛑 Cerrando {settings.service_name}")


def create_app() -> FastAPI:
    """Factory para crear la aplicación FastAPI unificada"""
    
    app = FastAPI(
        title="MediSupply Monolith API",
        description="API monolítica unificada de MediSupply - Todos los microservicios en una sola aplicación",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Incluir todos los routers con sus prefijos
    app.include_router(auth_router, prefix="/api/v1", tags=["authentication"])
    app.include_router(product_router, prefix="/api/v1", tags=["products"])
    app.include_router(order_router, prefix="/api/v1", tags=["orders"])
    app.include_router(logistics_router, prefix="/api/v1", tags=["logistics"])
    app.include_router(inventory_router, prefix="/api/v1", tags=["inventory"])
    app.include_router(reports_router, prefix="/api/v1", tags=["reports"])
    app.include_router(notifications_router, prefix="/api/v1", tags=["notifications"])
    
    @app.get("/")
    async def root():
        """Endpoint raíz"""
        return {
            "service": settings.service_name,
            "version": "1.0.0",
            "architecture": "monolith",
            "description": "Monolito unificado de MediSupply",
            "services": [
                "auth",
                "products",
                "orders",
                "logistics",
                "inventory",
                "reports",
                "notifications"
            ],
            "docs": "/docs"
        }
    
    @app.get("/health")
    async def health_check():
        """Health check"""
        return {
            "status": "healthy",
            "service": settings.service_name,
            "environment": settings.environment
        }
    
    return app


# Crear instancia de la aplicación
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.service_port
    )

