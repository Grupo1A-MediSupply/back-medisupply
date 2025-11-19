"""
Configuración de base de datos
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

try:
    from .config import get_settings
    from .repositories import Base
    # Importar modelos para asegurar que se registren en Base.metadata
    from .repositories import UserModel, VerificationCodeModel
except ImportError:
    from infrastructure.config import get_settings
    from infrastructure.repositories import Base
    # Importar modelos para asegurar que se registren en Base.metadata
    from infrastructure.repositories import UserModel, VerificationCodeModel

settings = get_settings()

# Motor de base de datos
# NOTA: No hacer logging aquí porque se ejecuta al importar el módulo
# y la variable de entorno puede no estar disponible aún
engine = create_engine(
    settings.database_url,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.debug
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency para obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Crear todas las tablas"""
    # Logging de configuración
    print(f"🔌 Configurando conexión a base de datos...")
    print(f"   URL: {settings.database_url[:100]}...")  # Mostrar primeros 100 caracteres
    print(f"   Usando SQLite: {'sqlite' in settings.database_url.lower()}")
    print(f"   Usando Cloud SQL: {'cloudsql' in settings.database_url.lower()}")
    
    # Probar la conexión antes de crear tablas
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print(f"✅ Conexión a base de datos exitosa")
            # Verificar qué base de datos estamos usando
            if "sqlite" not in settings.database_url.lower():
                try:
                    db_result = conn.execute(text("SELECT current_database()"))
                    db_name = db_result.scalar()
                    print(f"   Base de datos: {db_name}")
                except:
                    pass
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    # Verificar que hay modelos registrados
    table_names = list(Base.metadata.tables.keys())
    print(f"📊 Modelos registrados en Base.metadata: {len(table_names)}")
    if table_names:
        print(f"   Tablas: {', '.join(table_names)}")
    else:
        print("⚠️  ADVERTENCIA: No hay modelos registrados en Base.metadata")
        print("   Asegúrate de importar UserModel y VerificationCodeModel antes de llamar a create_tables()")
        return  # No continuar si no hay modelos
    
    try:
        Base.metadata.create_all(bind=engine)
        print(f"✅ create_all() ejecutado. Tablas a crear: {len(table_names)}")
        
        # Verificar que las tablas se crearon
        if "sqlite" not in settings.database_url.lower():
            try:
                from sqlalchemy import text, inspect
                inspector = inspect(engine)
                created_tables = inspector.get_table_names()
                print(f"✅ Tablas creadas en la base de datos: {len(created_tables)}")
                if created_tables:
                    print(f"   Tablas: {', '.join(created_tables)}")
            except Exception as e:
                print(f"⚠️  No se pudieron verificar las tablas creadas: {e}")
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")
        import traceback
        traceback.print_exc()
        raise

