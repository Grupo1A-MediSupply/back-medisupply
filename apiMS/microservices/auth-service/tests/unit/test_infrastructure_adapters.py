"""
Tests unitarios para adaptadores de infraestructura
"""
import pytest
from datetime import datetime, timedelta
import sys
from pathlib import Path
from unittest.mock import patch

# Agregar paths
auth_service_path = str(Path(__file__).parent.parent.parent)
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if auth_service_path not in sys.path:
    sys.path.insert(0, auth_service_path)
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from infrastructure.adapters import BcryptPasswordHasher, JWTTokenService


@pytest.mark.unit
class TestBcryptPasswordHasher:
    """Tests para BcryptPasswordHasher"""
    
    def test_init(self):
        """Test: Inicialización del hasher"""
        hasher = BcryptPasswordHasher()
        assert hasher.pwd_context is not None
    
    def test_hash_password(self):
        """Test: Hashear contraseña"""
        hasher = BcryptPasswordHasher()
        password = "TestPassword123!"
        
        hashed = hasher.hash_password(password)
        
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0
    
    def test_hash_password_different_results(self):
        """Test: Hashear la misma contraseña produce resultados diferentes"""
        hasher = BcryptPasswordHasher()
        password = "TestPassword123!"
        
        hashed1 = hasher.hash_password(password)
        hashed2 = hasher.hash_password(password)
        
        # Los hashes deben ser diferentes (salt diferente)
        assert hashed1 != hashed2
    
    def test_verify_password_correct(self):
        """Test: Verificar contraseña correcta"""
        hasher = BcryptPasswordHasher()
        password = "TestPassword123!"
        
        hashed = hasher.hash_password(password)
        result = hasher.verify_password(password, hashed)
        
        assert result is True
    
    def test_verify_password_incorrect(self):
        """Test: Verificar contraseña incorrecta"""
        hasher = BcryptPasswordHasher()
        password = "TestPassword123!"
        wrong_password = "WrongPassword456!"
        
        hashed = hasher.hash_password(password)
        result = hasher.verify_password(wrong_password, hashed)
        
        assert result is False
    
    def test_hash_password_long_password(self):
        """Test: Hashear contraseña muy larga (se trunca a 72 bytes)"""
        hasher = BcryptPasswordHasher()
        # Contraseña de más de 72 bytes
        long_password = "A" * 100
        
        hashed = hasher.hash_password(long_password)
        
        assert hashed is not None
        assert len(hashed) > 0
    
    def test_verify_password_long_password(self):
        """Test: Verificar contraseña muy larga"""
        hasher = BcryptPasswordHasher()
        long_password = "A" * 100
        
        hashed = hasher.hash_password(long_password)
        result = hasher.verify_password(long_password, hashed)
        
        assert result is True


@pytest.mark.unit
class TestJWTTokenService:
    """Tests para JWTTokenService"""
    
    def test_init(self):
        """Test: Inicialización del servicio JWT"""
        service = JWTTokenService(
            secret_key="test_secret",
            algorithm="HS256",
            access_token_expire_minutes=30
        )
        
        assert service.secret_key == "test_secret"
        assert service.algorithm == "HS256"
        assert service.access_token_expire_minutes == 30
    
    def test_init_default_values(self):
        """Test: Inicialización con valores por defecto"""
        service = JWTTokenService(secret_key="test_secret")
        
        assert service.secret_key == "test_secret"
        assert service.algorithm == "HS256"
        assert service.access_token_expire_minutes == 30
    
    def test_create_access_token(self):
        """Test: Crear token de acceso"""
        service = JWTTokenService(secret_key="test_secret")
        user_id = "123"
        username = "testuser"
        scopes = ["read", "write"]
        
        token = service.create_access_token(user_id, username, scopes)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_refresh_token(self):
        """Test: Crear token de refresco"""
        service = JWTTokenService(secret_key="test_secret")
        user_id = "123"
        username = "testuser"
        
        token = service.create_refresh_token(user_id, username)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_access_token_valid(self):
        """Test: Verificar token de acceso válido"""
        service = JWTTokenService(secret_key="test_secret")
        user_id = "123"
        username = "testuser"
        scopes = ["read", "write"]
        
        token = service.create_access_token(user_id, username, scopes)
        payload = service.verify_access_token(token)
        
        assert payload["sub"] == username
        assert payload["user_id"] == user_id
        assert payload["scopes"] == scopes
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload
    
    def test_verify_refresh_token_valid(self):
        """Test: Verificar token de refresco válido"""
        service = JWTTokenService(secret_key="test_secret")
        user_id = "123"
        username = "testuser"
        
        token = service.create_refresh_token(user_id, username)
        payload = service.verify_refresh_token(token)
        
        assert payload["sub"] == username
        assert payload["user_id"] == user_id
        assert payload["type"] == "refresh"
        assert "exp" in payload
        assert "iat" in payload
    
    def test_verify_access_token_invalid_token(self):
        """Test: Verificar token de acceso inválido"""
        service = JWTTokenService(secret_key="test_secret")
        
        with pytest.raises(ValueError, match="Token inválido"):
            service.verify_access_token("invalid_token")
    
    def test_verify_refresh_token_invalid_token(self):
        """Test: Verificar token de refresco inválido"""
        service = JWTTokenService(secret_key="test_secret")
        
        with pytest.raises(ValueError, match="Token inválido"):
            service.verify_refresh_token("invalid_token")
    
    def test_verify_access_token_wrong_type(self):
        """Test: Verificar token de acceso con tipo incorrecto"""
        service = JWTTokenService(secret_key="test_secret")
        user_id = "123"
        username = "testuser"
        
        # Crear refresh token pero intentar verificar como access token
        token = service.create_refresh_token(user_id, username)
        
        with pytest.raises(ValueError, match="Token de acceso requerido"):
            service.verify_access_token(token)
    
    def test_verify_refresh_token_wrong_type(self):
        """Test: Verificar token de refresco con tipo incorrecto"""
        service = JWTTokenService(secret_key="test_secret")
        user_id = "123"
        username = "testuser"
        scopes = ["read", "write"]
        
        # Crear access token pero intentar verificar como refresh token
        token = service.create_access_token(user_id, username, scopes)
        
        with pytest.raises(ValueError, match="Token de refresco requerido"):
            service.verify_refresh_token(token)
    
    def test_verify_access_token_expired(self):
        """Test: Verificar token de acceso expirado"""
        service = JWTTokenService(secret_key="test_secret", access_token_expire_minutes=-1)
        user_id = "123"
        username = "testuser"
        scopes = ["read", "write"]
        
        token = service.create_access_token(user_id, username, scopes)
        
        with pytest.raises(ValueError, match="Token expirado"):
            service.verify_access_token(token)
    
    def test_verify_refresh_token_expired(self):
        """Test: Verificar token de refresco expirado"""
        with patch('infrastructure.adapters.datetime') as mock_datetime:
            # Mock para simular token expirado
            mock_datetime.utcnow.return_value = datetime(2020, 1, 1)
            mock_datetime.timedelta = timedelta
            
            service = JWTTokenService(secret_key="test_secret")
            user_id = "123"
            username = "testuser"
            
            token = service.create_refresh_token(user_id, username)
            
            # Cambiar el tiempo para que el token esté expirado
            mock_datetime.utcnow.return_value = datetime(2030, 1, 1)
            
            with pytest.raises(ValueError, match="Token expirado"):
                service.verify_refresh_token(token)
    
    def test_different_secret_keys(self):
        """Test: Tokens creados con diferentes secret keys no son compatibles"""
        service1 = JWTTokenService(secret_key="secret1")
        service2 = JWTTokenService(secret_key="secret2")
        
        user_id = "123"
        username = "testuser"
        scopes = ["read", "write"]
        
        token = service1.create_access_token(user_id, username, scopes)
        
        with pytest.raises(ValueError, match="Token inválido"):
            service2.verify_access_token(token)
    
    def test_token_structure(self):
        """Test: Estructura del token de acceso"""
        service = JWTTokenService(secret_key="test_secret")
        user_id = "123"
        username = "testuser"
        scopes = ["read", "write"]
        
        token = service.create_access_token(user_id, username, scopes)
        payload = service.verify_access_token(token)
        
        # Verificar que todos los campos requeridos están presentes
        required_fields = ["sub", "user_id", "scopes", "exp", "iat", "type"]
        for field in required_fields:
            assert field in payload
        
        # Verificar tipos de datos
        assert isinstance(payload["sub"], str)
        assert isinstance(payload["user_id"], str)
        assert isinstance(payload["scopes"], list)
        assert isinstance(payload["exp"], (int, float))  # JWT decodifica fechas como timestamps
        assert isinstance(payload["iat"], (int, float))  # JWT decodifica fechas como timestamps
        assert isinstance(payload["type"], str)
