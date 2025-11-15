"""
Script para ejecutar el microservicio de autenticación
"""
import uvicorn
from main import app

# Configurar el PYTHONPATH correctamente
current_dir = Path(__file__).parent
microservices_dir = current_dir.parent
shared_dir = microservices_dir / "shared"

# Agregar paths al PYTHONPATH
sys.path.insert(0, str(microservices_dir))
sys.path.insert(0, str(shared_dir))
sys.path.insert(0, str(current_dir))

# Cambiar al directorio del auth-service
os.chdir(current_dir)

# Importar y ejecutar la aplicación
if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Iniciando Auth Service...")
    print(f"📁 Directorio de trabajo: {os.getcwd()}")
    print(f"🐍 Python path configurado correctamente")
    
    # Ejecutar como módulo Python desde el directorio microservices
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=False
    )

