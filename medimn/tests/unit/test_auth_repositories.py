"""
Tests unitarios para Auth Repositories
"""
import pytest
from datetime import datetime
from uuid import uuid4
from sqlalchemy.orm import Session

from auth.infrastructure.repositories import (
    SQLAlchemyUserRepository,
    UserModel,
    VerificationCodeModel
)
from shared.domain.value_objects import EntityId, Email
from auth.domain.value_objects import Username, HashedPassword
from auth.domain.entities import User


@pytest.mark.unit
class TestSQLAlchemyUserRepository:
    """Tests para SQLAlchemyUserRepository"""
    
    @pytest.mark.asyncio
    async def test_save_user(self, db_session: Session):
        """Test guardar usuario"""
        repo = SQLAlchemyUserRepository(db_session)
        
        user_id = EntityId(str(uuid4()))
        email = Email("test@example.com")
        username = Username("testuser")
        hashed_password = HashedPassword("$2b$12$hashedpassword")
        
        user = User.register(
            user_id=user_id,
            email=email,
            username=username,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False
        )
        
        saved_user = await repo.save(user)
        
        assert saved_user is not None
        assert saved_user.id == user_id
        
        # Verificar en base de datos
        db_user = db_session.query(UserModel).filter(UserModel.id == str(user_id)).first()
        assert db_user is not None
        assert db_user.email == "test@example.com"
        assert db_user.username == "testuser"
    
    @pytest.mark.asyncio
    async def test_find_by_id(self, db_session: Session):
        """Test buscar usuario por ID"""
        repo = SQLAlchemyUserRepository(db_session)
        
        # Crear usuario en BD
        user_id = str(uuid4())
        user_model = UserModel(
            id=user_id,
            email="test@example.com",
            username="testuser",
            hashed_password="$2b$12$hashedpassword",
            is_active=True,
            is_superuser=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(user_model)
        db_session.commit()
        
        # Buscar
        found_user = await repo.find_by_id(EntityId(user_id))
        
        assert found_user is not None
        assert str(found_user.id) == user_id
        assert str(found_user.email) == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_find_by_id_not_found(self, db_session: Session):
        """Test buscar usuario por ID no encontrado"""
        repo = SQLAlchemyUserRepository(db_session)
        
        found_user = await repo.find_by_id(EntityId("nonexistent-id"))
        
        assert found_user is None
    
    @pytest.mark.asyncio
    async def test_find_by_username(self, db_session: Session):
        """Test buscar usuario por username"""
        repo = SQLAlchemyUserRepository(db_session)
        
        # Crear usuario en BD
        user_id = str(uuid4())
        user_model = UserModel(
            id=user_id,
            email="test@example.com",
            username="testuser",
            hashed_password="$2b$12$hashedpassword",
            is_active=True,
            is_superuser=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(user_model)
        db_session.commit()
        
        # Buscar
        found_user = await repo.find_by_username(Username("testuser"))
        
        assert found_user is not None
        assert str(found_user.username) == "testuser"
    
    @pytest.mark.asyncio
    async def test_find_by_email(self, db_session: Session):
        """Test buscar usuario por email"""
        repo = SQLAlchemyUserRepository(db_session)
        
        # Crear usuario en BD
        user_id = str(uuid4())
        user_model = UserModel(
            id=user_id,
            email="test@example.com",
            username="testuser",
            hashed_password="$2b$12$hashedpassword",
            is_active=True,
            is_superuser=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(user_model)
        db_session.commit()
        
        # Buscar
        found_user = await repo.find_by_email(Email("test@example.com"))
        
        assert found_user is not None
        assert str(found_user.email) == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_exists_by_username(self, db_session: Session):
        """Test verificar existencia por username"""
        repo = SQLAlchemyUserRepository(db_session)
        
        # Crear usuario en BD
        user_model = UserModel(
            id=str(uuid4()),
            email="test@example.com",
            username="testuser",
            hashed_password="$2b$12$hashedpassword",
            is_active=True,
            is_superuser=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(user_model)
        db_session.commit()
        
        # Verificar existencia
        exists = await repo.exists_by_username(Username("testuser"))
        assert exists is True
        
        not_exists = await repo.exists_by_username(Username("nonexistent"))
        assert not_exists is False
    
    @pytest.mark.asyncio
    async def test_exists_by_email(self, db_session: Session):
        """Test verificar existencia por email"""
        repo = SQLAlchemyUserRepository(db_session)
        
        # Crear usuario en BD
        user_model = UserModel(
            id=str(uuid4()),
            email="test@example.com",
            username="testuser",
            hashed_password="$2b$12$hashedpassword",
            is_active=True,
            is_superuser=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(user_model)
        db_session.commit()
        
        # Verificar existencia
        exists = await repo.exists_by_email(Email("test@example.com"))
        assert exists is True
        
        not_exists = await repo.exists_by_email(Email("nonexistent@example.com"))
        assert not_exists is False
    
    @pytest.mark.asyncio
    async def test_delete_user(self, db_session: Session):
        """Test eliminar usuario"""
        repo = SQLAlchemyUserRepository(db_session)
        
        # Crear usuario en BD
        user_id = str(uuid4())
        user_model = UserModel(
            id=user_id,
            email="test@example.com",
            username="testuser",
            hashed_password="$2b$12$hashedpassword",
            is_active=True,
            is_superuser=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(user_model)
        db_session.commit()
        
        # Obtener usuario como entidad de dominio para verificar que existe
        user = await repo.find_by_id(EntityId(user_id))
        assert user is not None
        
        # Eliminar usando EntityId - el método delete retorna True si se eliminó
        result = await repo.delete(EntityId(user_id))
        
        # Verificar que retornó True
        assert result is True
        
        # Verificar que el usuario ya no existe en la BD
        deleted_user = await repo.find_by_id(EntityId(user_id))
        assert deleted_user is None

