"""
Tests unitarios para Domain Entities
"""
import pytest
from shared.domain.value_objects import EntityId, Email
from auth.domain.value_objects import Username, HashedPassword, FullName, PhoneNumber, UserRole, Address, InstitutionName
from auth.domain.entities import User


@pytest.mark.unit
class TestUserEntity:
    """Tests para User Entity"""
    
    def test_register_user(self):
        """Test registrar usuario"""
        user_id = EntityId("test-user-id")
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
        
        assert user is not None
        assert user.id == user_id
        assert user.email == email
        assert user.username == username
        assert user.is_active is True
    
    def test_user_deactivate(self):
        """Test desactivar usuario"""
        user_id = EntityId("test-user-id")
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
        
        user.deactivate()
        
        assert user.is_active is False
    
    def test_user_change_password(self):
        """Test cambiar contraseña"""
        user_id = EntityId("test-user-id")
        email = Email("test@example.com")
        username = Username("testuser")
        hashed_password = HashedPassword("$2b$12$oldpassword")
        new_hashed_password = HashedPassword("$2b$12$newpassword")
        
        user = User.register(
            user_id=user_id,
            email=email,
            username=username,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False
        )
        
        user.change_password(new_hashed_password)
        
        assert user.hashed_password == new_hashed_password
    
    def test_user_update_profile(self):
        """Test actualizar perfil"""
        user_id = EntityId("test-user-id")
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
        
        new_full_name = FullName("New Name")
        new_phone = PhoneNumber("+9876543210")
        
        user.update_profile(
            full_name=new_full_name,
            phone_number=new_phone
        )
        
        assert user.full_name == new_full_name
        assert user.phone_number == new_phone

