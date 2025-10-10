"""
Aplicación principal FastAPI - API de Autenticación
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import get_settings
from .database import create_tables
from .routes import router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    print(f"🚀 Iniciando API de Autenticación en {settings.environment}")
    create_tables()
    print("✅ Base de datos inicializada")
    
    yield
    
    # Shutdown
    print("🛑 Cerrando API de Autenticación")


def create_app() -> FastAPI:
    """Factory para crear la aplicación FastAPI"""
    
    app = FastAPI(
        title="API de Autenticación",
        description="Sistema de autenticación JWT con FastAPI",
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
    app.include_router(router, prefix=settings.api_v1_prefix, tags=["authentication"])
    
    @app.get("/")
    async def root():
        """Endpoint raíz"""
        return {
            "message": "API de Autenticación",
            "version": "1.0.0",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    
    @app.get("/health")
    async def health_check():
        """Endpoint de salud de la aplicación"""
        return {
            "status": "healthy", 
            "service": "auth-api",
            "environment": settings.environment
        }
    
    return app


# Crear instancia de la aplicación
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

