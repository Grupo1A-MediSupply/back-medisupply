#!/usr/bin/env python3
"""
Script para ejecutar el auth-service desde el directorio raíz del proyecto
"""
import sys
import os
from pathlib import Path

# Configurar el PYTHONPATH
current_dir = Path(__file__).parent
microservices_dir = current_dir / "apiMS" / "microservices"
shared_dir = microservices_dir / "shared"
auth_service_dir = microservices_dir / "auth-service"

# Agregar paths al PYTHONPATH
sys.path.insert(0, str(microservices_dir))
sys.path.insert(0, str(shared_dir))
sys.path.insert(0, str(auth_service_dir))

# Cambiar al directorio del auth-service
os.chdir(auth_service_dir)

print("🚀 Iniciando Auth Service...")
print(f"📁 Directorio de trabajo: {os.getcwd()}")
print(f"🐍 Python path configurado correctamente")

# Importar y ejecutar la aplicación
if __name__ == "__main__":
    import uvicorn
    
    # Ejecutar como módulo Python
    uvicorn.run(
        "auth-service.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
