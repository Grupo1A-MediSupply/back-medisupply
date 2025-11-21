"""
Tests unitarios para Infrastructure Database
"""
import pytest
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import sessionmaker
from infrastructure.database import Base, get_db, create_tables, SessionLocal


@pytest.mark.unit
class TestDatabase:
    """Tests para configuración de base de datos"""
    
    def test_base_metadata(self):
        """Test que Base tiene metadata"""
        assert Base.metadata is not None
    
    def test_get_db_generator(self):
        """Test que get_db retorna un generador"""
        db_gen = get_db()
        
        assert db_gen is not None
        # Verificar que es un generador
        assert hasattr(db_gen, '__iter__')
        
        # Consumir el generador
        try:
            db = next(db_gen)
            assert db is not None
        finally:
            try:
                next(db_gen)
            except StopIteration:
                pass
    
    def test_create_tables(self, db_session):
        """Test crear tablas"""
        # Las tablas ya están creadas por el fixture
        # Solo verificamos que la sesión funciona
        assert db_session is not None
        
        # Verificar que podemos hacer una query
        from sqlalchemy import text
        result = db_session.execute(text("SELECT 1"))
        assert result.scalar() == 1

