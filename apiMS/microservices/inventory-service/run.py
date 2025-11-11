"""
Script de ejecución del servicio de inventario
"""
import uvicorn
from main import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8005,
        reload=False
    )

