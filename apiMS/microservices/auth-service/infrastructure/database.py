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
    # Verificar que hay modelos registrados
    table_names = list(Base.metadata.tables.keys())
    print(f"📊 Modelos registrados en Base.metadata: {len(table_names)}")
    if table_names:
        print(f"   Tablas: {', '.join(table_names)}")
    else:
        print("⚠️  ADVERTENCIA: No hay modelos registrados en Base.metadata")
        print("   Asegúrate de importar UserModel y VerificationCodeModel antes de llamar a create_tables()")
    
    try:
        Base.metadata.create_all(bind=engine)
        print(f"✅ create_all() ejecutado. Tablas a crear: {len(table_names)}")
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")
        import traceback
        traceback.print_exc()
        raise

