"""
Script para ejecutar el microservicio de órdenes
"""
import uvicorn
from main import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8003,
        reload=False
    )

