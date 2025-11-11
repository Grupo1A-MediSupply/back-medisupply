"""
Configuración para tests
"""
import pytest
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Agregar paths al PYTHONPATH
order_service_path = str(Path(__file__).parent.parent.resolve())
shared_path = str(Path(__file__).parent.parent.parent.resolve() / "shared")
if order_service_path not in sys.path:
    sys.path.insert(0, order_service_path)
if shared_path not in sys.path:
    sys.path.insert(0, str(shared_path))

# Los imports se hacen dentro de las fixtures para evitar problemas cuando pytest carga el módulo

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_order_service.db"


@pytest.fixture
def db_session():
    """Fixture para sesión de base de datos de test"""
    from infrastructure.repositories import Base
    
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def order_repository(db_session):
    """Fixture para repositorio de órdenes"""
    from infrastructure.repositories import SQLAlchemyOrderRepository
    return SQLAlchemyOrderRepository(db_session)

