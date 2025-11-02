#!/usr/bin/env python3
"""
Script de inicio para el auth-service
"""
import sys
import os
from pathlib import Path

# Configurar el PYTHONPATH
current_dir = Path(__file__).parent
microservices_dir = current_dir.parent
shared_dir = microservices_dir / "shared"

# Agregar paths al PYTHONPATH
sys.path.insert(0, str(microservices_dir))
sys.path.insert(0, str(shared_dir))

# Cambiar al directorio del auth-service
os.chdir(current_dir)

# Importar y ejecutar la aplicación
if __name__ == "__main__":
    import uvicorn
    from main import app
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=True
    )
