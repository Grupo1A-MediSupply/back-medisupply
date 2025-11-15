"""
Tests unitarios para Value Objects del dominio de Auth
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

from shared.domain.value_objects import Email, EntityId
from domain.value_objects import Username, HashedPassword, FullName, PhoneNumber


@pytest.mark.unit
class TestEmail:
    """Tests para el Value Object Email"""
    
    def test_email_valido(self):
        """Test: Email válido se crea correctamente"""
        email = Email("test@example.com")
        assert email.value == "test@example.com"
        assert str(email) == "test@example.com"
    
    def test_email_invalido_sin_arroba(self):
        """Test: Email sin @ lanza excepción"""
        with pytest.raises(ValueError, match="Email inválido"):
            Email("testexample.com")
    
    def test_email_invalido_sin_dominio(self):
        """Test: Email sin dominio lanza excepción"""
        with pytest.raises(ValueError, match="Email inválido"):
            Email("test@")
    
    def test_email_es_inmutable(self):
        """Test: Email es inmutable"""
        email = Email("test@example.com")
        with pytest.raises(AttributeError):
            email.value = "otro@example.com"


@pytest.mark.unit
class TestUsername:
    """Tests para el Value Object Username"""
    
    def test_username_valido(self):
        """Test: Username válido se crea correctamente"""
        username = Username("testuser")
        assert username.value == "testuser"
        assert str(username) == "testuser"
    
    def test_username_muy_corto(self):
        """Test: Username menor a 3 caracteres lanza excepción"""
        with pytest.raises(ValueError, match="al menos 3 caracteres"):
            Username("ab")
    
    def test_username_muy_largo(self):
        """Test: Username mayor a 50 caracteres lanza excepción"""
        with pytest.raises(ValueError, match="no puede tener más de 50 caracteres"):
            Username("a" * 51)
    
    def test_username_minimo_permitido(self):
        """Test: Username de 3 caracteres es válido"""
        username = Username("abc")
        assert username.value == "abc"
    
    def test_username_maximo_permitido(self):
        """Test: Username de 50 caracteres es válido"""
        username = Username("a" * 50)
        assert len(username.value) == 50


@pytest.mark.unit
class TestHashedPassword:
    """Tests para el Value Object HashedPassword"""
    
    def test_hashed_password_valido(self):
        """Test: HashedPassword válido se crea correctamente"""
        hashed = HashedPassword("$2b$12$KIXxkXvHVvH3HQvK5l3Jae")
        assert hashed.value == "$2b$12$KIXxkXvHVvH3HQvK5l3Jae"
    
    def test_hashed_password_vacio(self):
        """Test: HashedPassword vacío lanza excepción"""
        with pytest.raises(ValueError, match="no puede estar vacía"):
            HashedPassword("")
    
    def test_hashed_password_none(self):
        """Test: HashedPassword None lanza excepción"""
        with pytest.raises(ValueError):
            HashedPassword(None)


@pytest.mark.unit
class TestFullName:
    """Tests para el Value Object FullName"""
    
    def test_full_name_valido(self):
        """Test: FullName válido se crea correctamente"""
        name = FullName("John Doe")
        assert name.value == "John Doe"
        assert str(name) == "John Doe"
    
    def test_full_name_vacio(self):
        """Test: FullName vacío es válido"""
        name = FullName("")
        assert str(name) == ""
    
    def test_full_name_none(self):
        """Test: FullName None es válido"""
        name = FullName(None)
        assert str(name) == ""
    
    def test_full_name_muy_largo(self):
        """Test: FullName mayor a 100 caracteres lanza excepción"""
        with pytest.raises(ValueError, match="no puede tener más de 100 caracteres"):
            FullName("a" * 101)


@pytest.mark.unit
class TestEntityId:
    """Tests para el Value Object EntityId"""
    
    def test_entity_id_valido(self):
        """Test: EntityId válido se crea correctamente"""
        entity_id = EntityId("123e4567-e89b-12d3-a456-426614174000")
        assert entity_id.value == "123e4567-e89b-12d3-a456-426614174000"
    
    def test_entity_id_vacio(self):
        """Test: EntityId vacío lanza excepción"""
        with pytest.raises(ValueError, match="no puede estar vacío"):
            EntityId("")
    
    def test_entity_id_igualdad(self):
        """Test: Dos EntityId con mismo valor son iguales"""
        id1 = EntityId("123")
        id2 = EntityId("123")
        assert id1 == id2
    
    def test_entity_id_hash(self):
        """Test: EntityId puede usarse en sets/dicts"""
        id1 = EntityId("123")
        id2 = EntityId("123")
        assert hash(id1) == hash(id2)
        
        # Puede usarse en set
        ids_set = {id1, id2}
        assert len(ids_set) == 1


@pytest.mark.unit
class TestPhoneNumber:
    """Tests para el Value Object PhoneNumber"""
    
    def test_phone_number_valido(self):
        """Test: PhoneNumber válido se crea correctamente"""
        phone = PhoneNumber("+1234567890")
        assert phone.value == "+1234567890"
        assert str(phone) == "+1234567890"
    
    def test_phone_number_sin_prefijo(self):
        """Test: PhoneNumber sin prefijo + es válido"""
        phone = PhoneNumber("1234567890")
        assert phone.value == "1234567890"
    
    def test_phone_number_con_espacios(self):
        """Test: PhoneNumber con espacios es válido"""
        phone = PhoneNumber("+1 234 567 890")
        assert phone.value == "+1 234 567 890"
    
    def test_phone_number_con_guiones(self):
        """Test: PhoneNumber con guiones es válido"""
        phone = PhoneNumber("+1-234-567-890")
        assert phone.value == "+1-234-567-890"
    
    def test_phone_number_con_parentesis(self):
        """Test: PhoneNumber con paréntesis es válido"""
        phone = PhoneNumber("+1 (234) 567-890")
        assert phone.value == "+1 (234) 567-890"
    
    def test_phone_number_vacio(self):
        """Test: PhoneNumber vacío lanza excepción"""
        with pytest.raises(ValueError, match="no puede estar vacío"):
            PhoneNumber("")
    
    def test_phone_number_muy_corto(self):
        """Test: PhoneNumber menor a 7 caracteres lanza excepción"""
        with pytest.raises(ValueError, match="formato del número de teléfono no es válido"):
            PhoneNumber("123456")
    
    def test_phone_number_muy_largo(self):
        """Test: PhoneNumber mayor a 15 caracteres lanza excepción"""
        with pytest.raises(ValueError, match="formato del número de teléfono no es válido"):
            PhoneNumber("+1234567890123456")
    
    def test_phone_number_con_caracteres_invalidos(self):
        """Test: PhoneNumber con caracteres inválidos lanza excepción"""
        with pytest.raises(ValueError, match="formato del número de teléfono no es válido"):
            PhoneNumber("+123-abc-567")
    
    def test_phone_number_es_inmutable(self):
        """Test: PhoneNumber es inmutable"""
        phone = PhoneNumber("+1234567890")
        with pytest.raises(AttributeError):
            phone.value = "+0987654321"

