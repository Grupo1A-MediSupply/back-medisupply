"""
Aplicación principal del microservicio de notificaciones
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .infrastructure.config import get_settings
from .api.routes import router

settings = get_settings()


def create_app() -> FastAPI:
    """Factory para crear la aplicación FastAPI"""
    
    app = FastAPI(
        title="Notifications Service",
        description="Microservicio de notificaciones con arquitectura hexagonal",
        version="1.0.0",
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url="/redoc" if settings.environment != "production" else None
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
    app.include_router(router, prefix="/api/v1", tags=["notifications"])
    app.include_router(router, prefix="/api", tags=["notifications"])
    
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

