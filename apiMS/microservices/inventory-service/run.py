"""
Script de ejecución del servicio de inventario
"""
import uvicorn
from .infrastructure.config import get_settings

settings = get_settings()

if __name__ == "__main__":
    uvicorn.run(
        "inventory_service.main:app",
        host="0.0.0.0",
        port=settings.service_port,
        reload=True
    )

