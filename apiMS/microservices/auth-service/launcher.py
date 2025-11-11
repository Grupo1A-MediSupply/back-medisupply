#!/usr/bin/env python
"""
Launcher script para el microservicio de autenticación
Este script configura el entorno correctamente y ejecuta el servicio
"""
import sys
import os
import importlib.util

# Configurar el directorio de trabajo
service_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(service_dir)

# Agregar directorios al path
sys.path.insert(0, app_dir)
sys.path.insert(0, service_dir)

# Cambiar al directorio del servicio
os.chdir(service_dir)

# Configurar __package__ para que los imports relativos funcionen
import __main__
__main__.__package__ = 'auth_service_module'

# Importar manualmente los módulos necesarios con imports absolutos
import infrastructure.config
import infrastructure.database
import api.routes
import application.services

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

settings = infrastructure.config.get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    print(f"🚀 Iniciando {settings.service_name} en {settings.environment}")
    infrastructure.database.create_tables()
    print("✅ Base de datos inicializada")
    
    # Configurar event handlers
    event_handler = application.services.UserEventHandler()
    application.services.setup_event_handlers(event_handler)
    print("✅ Event handlers configurados")
    
    yield
    
    # Shutdown
    print(f"🛑 Cerrando {settings.service_name}")


# Crear la aplicación
app = FastAPI(
    title="Auth Service",
    description="Microservicio de autenticación con arquitectura hexagonal",
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
app.include_router(api.routes.router, prefix="/api/v1", tags=["authentication"])
app.include_router(api.routes.router, prefix="/api", tags=["authentication"])


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


# Ejecutar con uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
