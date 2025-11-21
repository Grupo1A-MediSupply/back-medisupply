"""
Configuración de base de datos unificada para el monolito
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from .config import get_settings

settings = get_settings()

# Base declarativa unificada
Base = declarative_base()

# Motor de base de datos
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
    """Crear todas las tablas de todos los servicios"""
    print(f"🔌 Configurando conexión a base de datos unificada...")
    print(f"   URL: {settings.database_url[:100]}...")
    
    # Importar todos los modelos para que se registren en Base.metadata
    # Esto se hará dinámicamente cuando se importen los módulos de cada servicio
    
    try:
        # Probar la conexión
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print(f"✅ Conexión a base de datos exitosa")
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos: {e}")
        raise
    
    # Verificar modelos registrados
    table_names = list(Base.metadata.tables.keys())
    print(f"📊 Modelos registrados: {len(table_names)}")
    if table_names:
        print(f"   Tablas: {', '.join(table_names)}")
    
    try:
        Base.metadata.create_all(bind=engine)
        print(f"✅ Tablas creadas exitosamente")
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")
        raise

