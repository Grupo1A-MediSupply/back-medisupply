#!/usr/bin/env python3
"""
Script para validar que el backend está guardando correctamente en Cloud SQL
Prueba operaciones CRUD básicas en cada base de datos
"""
import os
import sys
import subprocess
from datetime import datetime
from typing import Optional

try:
    import psycopg2
    from psycopg2 import sql
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
except ImportError:
    print("❌ psycopg2 no está instalado. Instálalo con: pip install psycopg2-binary")
    sys.exit(1)

# Configuración
PROJECT_ID = "project-65436llm"
INSTANCE_NAME = "project-65436llm-postgres-instance"
REGION = "us-central1"

# Configuración de bases de datos y usuarios
DATABASES = {
    "auth_service": {
        "user": "auth_service_user",
        "secret": "auth-service-db-password",
        "test_table": "test_validation"
    },
    "product_service": {
        "user": "product_service_user",
        "secret": "product-service-db-password",
        "test_table": "test_validation"
    },
    "order_service": {
        "user": "order_service_user",
        "secret": "order-service-db-password",
        "test_table": "test_validation"
    },
    "logistics_service": {
        "user": "logistics_service_user",
        "secret": "logistics-service-db-password",
        "test_table": "test_validation"
    },
    "notifications_service": {
        "user": "notifications_service_user",
        "secret": "notifications-service-db-password",
        "test_table": "test_validation"
    }
}

# Colores para output
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'


def get_password(secret_name: str) -> Optional[str]:
    """Obtener contraseña de Secret Manager"""
    try:
        result = subprocess.run(
            ["gcloud", "secrets", "versions", "access", "latest", f"--secret={secret_name}"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        print(f"{Colors.YELLOW}⚠️  No se pudo obtener la contraseña de {secret_name}{Colors.NC}")
        return None


def test_connection(db_name: str, user: str, password: str, host: str = "127.0.0.1", port: int = 5432) -> bool:
    """Probar conexión a la base de datos"""
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=db_name,
            user=user,
            password=password,
            connect_timeout=5
        )
        conn.close()
        return True
    except psycopg2.Error as e:
        print(f"{Colors.RED}❌ Error de conexión: {e}{Colors.NC}")
        return False


def test_crud_operations(db_name: str, user: str, password: str, table_name: str, host: str = "127.0.0.1", port: int = 5432) -> bool:
    """Probar operaciones CRUD básicas"""
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=db_name,
            user=user,
            password=password,
            connect_timeout=5
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # CREATE: Crear tabla de prueba
        print(f"  {Colors.BLUE}→ Creando tabla de prueba...{Colors.NC}")
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                test_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # INSERT: Insertar un registro
        print(f"  {Colors.BLUE}→ Insertando registro de prueba...{Colors.NC}")
        test_data = f"Test validation - {datetime.now().isoformat()}"
        cursor.execute(
            f"INSERT INTO {table_name} (test_data) VALUES (%s) RETURNING id",
            (test_data,)
        )
        inserted_id = cursor.fetchone()[0]
        print(f"  {Colors.GREEN}✅ Registro insertado con ID: {inserted_id}{Colors.NC}")
        
        # READ: Leer el registro
        print(f"  {Colors.BLUE}→ Leyendo registro...{Colors.NC}")
        cursor.execute(f"SELECT * FROM {table_name} WHERE id = %s", (inserted_id,))
        row = cursor.fetchone()
        if row:
            print(f"  {Colors.GREEN}✅ Registro leído: {row}{Colors.NC}")
        else:
            print(f"  {Colors.RED}❌ No se pudo leer el registro{Colors.NC}")
            return False
        
        # UPDATE: Actualizar el registro
        print(f"  {Colors.BLUE}→ Actualizando registro...{Colors.NC}")
        updated_data = f"Updated - {datetime.now().isoformat()}"
        cursor.execute(
            f"UPDATE {table_name} SET test_data = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (updated_data, inserted_id)
        )
        if cursor.rowcount > 0:
            print(f"  {Colors.GREEN}✅ Registro actualizado{Colors.NC}")
        else:
            print(f"  {Colors.RED}❌ No se pudo actualizar el registro{Colors.NC}")
            return False
        
        # Verificar la actualización
        cursor.execute(f"SELECT test_data FROM {table_name} WHERE id = %s", (inserted_id,))
        updated_row = cursor.fetchone()
        if updated_row and updated_data in updated_row[0]:
            print(f"  {Colors.GREEN}✅ Actualización verificada{Colors.NC}")
        else:
            print(f"  {Colors.RED}❌ La actualización no se guardó correctamente{Colors.NC}")
            return False
        
        # DELETE: Eliminar el registro
        print(f"  {Colors.BLUE}→ Eliminando registro de prueba...{Colors.NC}")
        cursor.execute(f"DELETE FROM {table_name} WHERE id = %s", (inserted_id,))
        if cursor.rowcount > 0:
            print(f"  {Colors.GREEN}✅ Registro eliminado{Colors.NC}")
        else:
            print(f"  {Colors.RED}❌ No se pudo eliminar el registro{Colors.NC}")
            return False
        
        # Limpiar: Eliminar tabla de prueba
        print(f"  {Colors.BLUE}→ Limpiando tabla de prueba...{Colors.NC}")
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        print(f"  {Colors.GREEN}✅ Tabla eliminada{Colors.NC}")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"  {Colors.RED}❌ Error en operaciones CRUD: {e}{Colors.NC}")
        return False


def main():
    print(f"{Colors.BLUE}========================================{Colors.NC}")
    print(f"{Colors.BLUE}Validación de Operaciones en Cloud SQL{Colors.NC}")
    print(f"{Colors.BLUE}========================================{Colors.NC}")
    print()
    
    # Verificar que Cloud SQL Proxy esté corriendo
    print(f"{Colors.YELLOW}⚠️  IMPORTANTE: Asegúrate de que Cloud SQL Proxy esté corriendo{Colors.NC}")
    print(f"{Colors.YELLOW}   Ejecuta en otra terminal: cloud-sql-proxy {PROJECT_ID}:{REGION}:{INSTANCE_NAME}{Colors.NC}")
    print()
    
    input("Presiona Enter cuando el proxy esté corriendo...")
    print()
    
    results = {}
    
    for db_name, config in DATABASES.items():
        print(f"{Colors.BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.NC}")
        print(f"{Colors.BLUE}Probando: {db_name}{Colors.NC}")
        print(f"{Colors.BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.NC}")
        
        # Obtener contraseña
        password = get_password(config["secret"])
        if not password:
            print(f"{Colors.RED}❌ No se pudo obtener la contraseña. Saltando...{Colors.NC}")
            results[db_name] = False
            print()
            continue
        
        # Probar conexión
        print(f"{Colors.BLUE}[1/2] Probando conexión...{Colors.NC}")
        if not test_connection(db_name, config["user"], password):
            print(f"{Colors.RED}❌ Falló la conexión{Colors.NC}")
            results[db_name] = False
            print()
            continue
        print(f"{Colors.GREEN}✅ Conexión exitosa{Colors.NC}")
        print()
        
        # Probar operaciones CRUD
        print(f"{Colors.BLUE}[2/2] Probando operaciones CRUD...{Colors.NC}")
        if test_crud_operations(db_name, config["user"], password, config["test_table"]):
            print(f"{Colors.GREEN}✅ Todas las operaciones CRUD funcionaron correctamente{Colors.NC}")
            results[db_name] = True
        else:
            print(f"{Colors.RED}❌ Fallaron algunas operaciones CRUD{Colors.NC}")
            results[db_name] = False
        
        print()
    
    # Resumen
    print(f"{Colors.BLUE}========================================{Colors.NC}")
    print(f"{Colors.BLUE}Resumen de Validación{Colors.NC}")
    print(f"{Colors.BLUE}========================================{Colors.NC}")
    print()
    
    all_passed = True
    for db_name, passed in results.items():
        status = f"{Colors.GREEN}✅ PASS{Colors.NC}" if passed else f"{Colors.RED}❌ FAIL{Colors.NC}"
        print(f"  {db_name:30} {status}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print(f"{Colors.GREEN}✅ Todas las validaciones pasaron correctamente{Colors.NC}")
        print(f"{Colors.GREEN}   El backend está guardando correctamente en Cloud SQL{Colors.NC}")
    else:
        print(f"{Colors.RED}❌ Algunas validaciones fallaron{Colors.NC}")
        print(f"{Colors.YELLOW}   Revisa los errores arriba y verifica la configuración{Colors.NC}")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

