#!/usr/bin/env python3
"""
Script para ejecutar la aplicación API de Autenticación
"""
import os
import sys
import subprocess
from pathlib import Path


def setup_environment():
    """Configurar variables de entorno"""
    env_vars = {
        "ENVIRONMENT": "development",
        "DEBUG": "true",
        "DATABASE_URL": "sqlite:///./auth_api.db",
        "SECRET_KEY": "dev-secret-key-change-in-production-12345",
        "ALGORITHM": "HS256",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
        "ALLOWED_ORIGINS": '["http://localhost:3000", "http://localhost:8080", "http://localhost:8000"]'
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value


def install_dependencies():
    """Instalar dependencias si es necesario"""
    try:
        import fastapi
        import uvicorn
        print("✅ Dependencias ya instaladas")
    except ImportError:
        print("📦 Instalando dependencias...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])


def create_database():
    """Crear base de datos SQLite"""
    db_path = Path("auth_api.db")
    if not db_path.exists():
        print("🗄️  Creando base de datos SQLite...")
        try:
            subprocess.run([sys.executable, "init_db.py"])
        except Exception as e:
            print(f"⚠️  Error al crear la base de datos: {e}")
            print("La base de datos se creará automáticamente al iniciar la aplicación")
    else:
        print("✅ Base de datos ya existe")


def run_application():
    """Ejecutar la aplicación"""
    print("🚀 Iniciando API de Autenticación...")
    print("📚 Documentación disponible en: http://localhost:8000/docs")
    print("🔄 ReDoc disponible en: http://localhost:8000/redoc")
    print("🛑 Presiona Ctrl+C para detener")
    print("")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Aplicación detenida")


if __name__ == "__main__":
    print("🔐 API de Autenticación JWT - FastAPI")
    print("=" * 60)
    
    setup_environment()
    install_dependencies()
    create_database()
    run_application()

