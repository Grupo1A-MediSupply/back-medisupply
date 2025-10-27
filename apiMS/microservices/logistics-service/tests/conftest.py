"""
Configuración para tests
"""
import pytest
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from ...infrastructure.repositories import SQLAlchemyLogisticsRepository, Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_logistics_service.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Fixture para sesión de base de datos de test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def logistics_repository(db_session):
    """Fixture para repositorio de logística"""
    return SQLAlchemyLogisticsRepository(db_session)

