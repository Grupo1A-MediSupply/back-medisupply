"""
Configuración para tests
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..infrastructure.repositories import SQLAlchemyOrderRepository, Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_order_service.db"

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
def order_repository(db_session):
    """Fixture para repositorio de órdenes"""
    return SQLAlchemyOrderRepository(db_session)

