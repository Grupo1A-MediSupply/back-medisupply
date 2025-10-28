"""
Script de inicio para el microservicio de autenticación
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app_wrapper:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )
