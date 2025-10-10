#!/usr/bin/env python3
"""
Script para inicializar la base de datos
"""
from app.database import engine, Base, create_tables
from app.models import User

def init_database():
    """Inicializar base de datos"""
    print("🗄️  Creando tablas de la base de datos...")
    
    # Crear todas las tablas
    create_tables()
    
    print("✅ Base de datos inicializada exitosamente")
    print("📝 Tablas creadas:")
    print("   - users")


if __name__ == "__main__":
    init_database()

