"""
Tests unitarios para entidades del dominio de Auth
"""
import pytest
import sys
from pathlib import Path

# Agregar paths
auth_service_path = str(Path(__file__).parent.parent.parent)
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if auth_service_path not in sys.path:
    sys.path.insert(0, auth_service_path)
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from shared.domain.value_objects import EntityId, Email
from domain.value_objects import Username, HashedPassword, FullName, PhoneNumber
from domain.entities import User
from domain.events import UserRegisteredEvent, UserLoggedInEvent, UserDeactivatedEvent


@pytest.mark.unit
class TestUserEntity:
    """Tests para la entidad User"""
    
    def test_crear_usuario(self):
        """Test: Usuario se crea correctamente"""
        user = User(
            user_id=EntityId("123"),
            email=Email("test@example.com"),
            username=Username("testuser"),
            hashed_password=HashedPassword("$2b$12$hash"),
            full_name=FullName("Test User"),
            phone_number=PhoneNumber("+1234567890"),
            is_active=True,
            is_superuser=False
        )
        
        assert str(user.id) == "123"
        assert str(user.email) == "test@example.com"
        assert str(user.username) == "testuser"
        assert str(user.full_name) == "Test User"
        assert str(user.phone_number) == "+1234567890"
        assert user.is_active is True
        assert user.is_superuser is False
    
    def test_register_factory_method(self):
        """Test: Factory method register crea usuario y registra evento"""
        user = User.register(
            user_id=EntityId("123"),
            email=Email("test@example.com"),
            username=Username("testuser"),
            hashed_password=HashedPassword("$2b$12$hash"),
            full_name=FullName("Test User")
        )
        
        # Verificar usuario creado
        assert str(user.id) == "123"
        assert str(user.email) == "test@example.com"
        
        # Verificar evento registrado
        events = user.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], UserRegisteredEvent)
        assert events[0].user_id == "123"
        assert events[0].username == "testuser"
        assert events[0].email == "test@example.com"
    
    def test_login_registra_evento(self):
        """Test: Login registra evento de dominio"""
        user = User(
            user_id=EntityId("123"),
            email=Email("test@example.com"),
            username=Username("testuser"),
            hashed_password=HashedPassword("$2b$12$hash"),
            is_active=True
        )
        
        user.login()
        
        events = user.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], UserLoggedInEvent)
        assert events[0].user_id == "123"
        assert events[0].username == "testuser"
    
    def test_login_usuario_inactivo_lanza_error(self):
        """Test: Login de usuario inactivo lanza excepción"""
        user = User(
            user_id=EntityId("123"),
            email=Email("test@example.com"),
            username=Username("testuser"),
            hashed_password=HashedPassword("$2b$12$hash"),
            is_active=False
        )
        
        with pytest.raises(ValueError, match="desactivado"):
            user.login()
    
    def test_deactivate_usuario(self):
        """Test: Desactivar usuario cambia estado y registra evento"""
        user = User(
            user_id=EntityId("123"),
            email=Email("test@example.com"),
            username=Username("testuser"),
            hashed_password=HashedPassword("$2b$12$hash"),
            is_active=True
        )
        
        user.deactivate()
        
        assert user.is_active is False
        events = user.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], UserDeactivatedEvent)
    
    def test_deactivate_usuario_ya_inactivo_lanza_error(self):
        """Test: Desactivar usuario ya inactivo lanza excepción"""
        user = User(
            user_id=EntityId("123"),
            email=Email("test@example.com"),
            username=Username("testuser"),
            hashed_password=HashedPassword("$2b$12$hash"),
            is_active=False
        )
        
        with pytest.raises(ValueError, match="ya está desactivado"):
            user.deactivate()
    
    def test_activate_usuario(self):
        """Test: Activar usuario cambia estado"""
        user = User(
            user_id=EntityId("123"),
            email=Email("test@example.com"),
            username=Username("testuser"),
            hashed_password=HashedPassword("$2b$12$hash"),
            is_active=False
        )
        
        user.activate()
        
        assert user.is_active is True
    
    def test_activate_usuario_ya_activo_lanza_error(self):
        """Test: Activar usuario ya activo lanza excepción"""
        user = User(
            user_id=EntityId("123"),
            email=Email("test@example.com"),
            username=Username("testuser"),
            hashed_password=HashedPassword("$2b$12$hash"),
            is_active=True
        )
        
        with pytest.raises(ValueError, match="ya está activo"):
            user.activate()
    
    def test_change_password(self):
        """Test: Cambiar contraseña actualiza el hash"""
        user = User(
            user_id=EntityId("123"),
            email=Email("test@example.com"),
            username=Username("testuser"),
            hashed_password=HashedPassword("$2b$12$old_hash"),
            is_active=True
        )
        
        new_password = HashedPassword("$2b$12$new_hash")
        user.change_password(new_password)
        
        assert str(user.hashed_password) == "$2b$12$new_hash"
    
    def test_update_profile(self):
        """Test: Actualizar perfil cambia nombre y teléfono"""
        user = User(
            user_id=EntityId("123"),
            email=Email("test@example.com"),
            username=Username("testuser"),
            hashed_password=HashedPassword("$2b$12$hash"),
            full_name=FullName("Old Name"),
            phone_number=PhoneNumber("+1111111111"),
            is_active=True
        )
        
        user.update_profile(
            full_name=FullName("New Name"),
            phone_number=PhoneNumber("+2222222222")
        )
        
        assert str(user.full_name) == "New Name"
        assert str(user.phone_number) == "+2222222222"
    
    def test_update_profile_solo_nombre(self):
        """Test: Actualizar perfil solo con nombre"""
        user = User(
            user_id=EntityId("123"),
            email=Email("test@example.com"),
            username=Username("testuser"),
            hashed_password=HashedPassword("$2b$12$hash"),
            full_name=FullName("Old Name"),
            phone_number=PhoneNumber("+1111111111"),
            is_active=True
        )
        
        user.update_profile(full_name=FullName("New Name"))
        
        assert str(user.full_name) == "New Name"
        assert str(user.phone_number) == "+1111111111"  # No cambia
    
    def test_update_profile_solo_telefono(self):
        """Test: Actualizar perfil solo con teléfono"""
        user = User(
            user_id=EntityId("123"),
            email=Email("test@example.com"),
            username=Username("testuser"),
            hashed_password=HashedPassword("$2b$12$hash"),
            full_name=FullName("Old Name"),
            phone_number=PhoneNumber("+1111111111"),
            is_active=True
        )
        
        user.update_profile(phone_number=PhoneNumber("+2222222222"))
        
        assert str(user.full_name) == "Old Name"  # No cambia
        assert str(user.phone_number) == "+2222222222"
    
    def test_clear_domain_events(self):
        """Test: Clear limpia los eventos de dominio"""
        user = User.register(
            user_id=EntityId("123"),
            email=Email("test@example.com"),
            username=Username("testuser"),
            hashed_password=HashedPassword("$2b$12$hash")
        )
        
        assert len(user.get_domain_events()) == 1
        
        user.clear_domain_events()
        
        assert len(user.get_domain_events()) == 0
    
    def test_user_equality(self):
        """Test: Dos usuarios con mismo ID son iguales"""
        user1 = User(
            user_id=EntityId("123"),
            email=Email("test1@example.com"),
            username=Username("user1"),
            hashed_password=HashedPassword("$2b$12$hash1")
        )
        
        user2 = User(
            user_id=EntityId("123"),
            email=Email("test2@example.com"),
            username=Username("user2"),
            hashed_password=HashedPassword("$2b$12$hash2")
        )
        
        assert user1 == user2
    
    def test_user_hash(self):
        """Test: Usuario puede usarse en sets/dicts"""
        user = User(
            user_id=EntityId("123"),
            email=Email("test@example.com"),
            username=Username("testuser"),
            hashed_password=HashedPassword("$2b$12$hash")
        )
        
        users_set = {user}
        assert len(users_set) == 1

