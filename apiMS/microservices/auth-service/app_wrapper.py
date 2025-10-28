"""
Wrapper para la aplicación que maneja imports relativos
"""
import sys
import os

# Configurar el path de Python
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Importar configuración y módulos necesarios
from infrastructure.config import get_settings
from infrastructure.database import create_tables
from api.routes import router
from application.services import UserEventHandler, setup_event_handlers

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    print(f"🚀 Iniciando {settings.service_name} en {settings.environment}")
    create_tables()
    print("✅ Base de datos inicializada")
    
    # Configurar event handlers
    event_handler = UserEventHandler()
    setup_event_handlers(event_handler)
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
app.include_router(router, prefix="/api/v1", tags=["authentication"])
app.include_router(router, prefix="/api", tags=["authentication"])


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

