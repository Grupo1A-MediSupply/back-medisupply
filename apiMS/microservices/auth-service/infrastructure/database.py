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

# Engine y SessionLocal se inicializarán de forma lazy cuando se necesiten
_engine = None
_SessionLocal = None


def _init_database():
    """Inicializar engine y SessionLocal, leyendo directamente las variables de entorno"""
    global _engine, _SessionLocal
    
    # Leer directamente de variables de entorno en lugar de usar el singleton
    # Esto asegura que siempre leamos los valores más actuales
    import os
    
    # Leer AUTH_DATABASE_URL directamente de os.environ
    database_url = os.environ.get(
        "AUTH_DATABASE_URL",
        "sqlite:///./auth_service.db"  # Valor por defecto
    )
    
    # Leer DEBUG también
    debug_str = os.environ.get("DEBUG", "false")
    debug = debug_str.lower() in ("true", "1", "yes")
    
    # Logging para diagnóstico
    print(f"🔍 _init_database() - Leyendo variables de entorno directamente")
    print(f"   AUTH_DATABASE_URL presente: {bool(os.environ.get('AUTH_DATABASE_URL'))}")
    print(f"   URL leída: {database_url[:100]}...")
    
    # Crear engine y SessionLocal con la URL leída directamente
    _engine = create_engine(
        database_url,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False} if "sqlite" in database_url.lower() else {},
        echo=debug
    )
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    return _engine, _SessionLocal


def __getattr__(name):
    """Permitir acceso lazy a engine y SessionLocal"""
    global _engine, _SessionLocal
    if name == 'engine':
        if _engine is None:
            _engine, _SessionLocal = _init_database()
        return _engine
    elif name == 'SessionLocal':
        if _SessionLocal is None:
            _engine, _SessionLocal = _init_database()
        return _SessionLocal
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def get_db():
    """Dependency para obtener sesión de base de datos"""
    # Acceso lazy a SessionLocal
    if _SessionLocal is None:
        _init_database()
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Crear todas las tablas"""
    # Inicializar engine y SessionLocal leyendo directamente de variables de entorno
    engine, _ = _init_database()
    
    # Leer URL directamente de variables de entorno para logging
    import os
    database_url = os.environ.get(
        "AUTH_DATABASE_URL",
        "sqlite:///./auth_service.db"
    )
    
    # Logging de configuración
    print(f"🔌 Configurando conexión a base de datos...")
    print(f"   URL: {database_url[:100]}...")  # Mostrar primeros 100 caracteres
    print(f"   Usando SQLite: {'sqlite' in database_url.lower()}")
    print(f"   Usando Cloud SQL: {'cloudsql' in database_url.lower() or '/cloudsql/' in database_url}")
    
    # Probar la conexión antes de crear tablas
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print(f"✅ Conexión a base de datos exitosa")
            # Verificar qué base de datos estamos usando
            if "sqlite" not in database_url.lower():
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
        if "sqlite" not in database_url.lower():
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
