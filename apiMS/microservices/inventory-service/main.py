"""
Aplicación principal del microservicio de inventario
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .infrastructure.config import get_settings
from .infrastructure.database import create_tables
from .api.routes import router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    print(f"🚀 Iniciando {settings.service_name} en {settings.environment}")
    create_tables()
    print("✅ Base de datos inicializada")
    
    yield
    
    # Shutdown
    print(f"🛑 Cerrando {settings.service_name}")


def create_app() -> FastAPI:
    """Factory para crear la aplicación FastAPI"""
    
    app = FastAPI(
        title="Inventory Service",
        description="Microservicio de inventario con arquitectura hexagonal",
        version="1.0.0",
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url="/redoc" if settings.environment != "production" else None,
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
    
    # Incluir routers
    app.include_router(router, prefix="/api/v1", tags=["inventory"])
    app.include_router(router, prefix="/api", tags=["inventory"])
    
    @app.get("/")
    async def root():
        """Endpoint raíz"""
        return {
            "service": settings.service_name,
            "version": "1.0.0",
            "architecture": "hexagonal",
            "patterns": ["CQRS", "Event-Driven", "DDD"],
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

