"""
Tests unitarios para Auth Adapters (Password Hasher, Token Service)
"""
import pytest
from datetime import datetime, timedelta
import jwt
from unittest.mock import patch

from auth.infrastructure.adapters import BcryptPasswordHasher, JWTTokenService


@pytest.mark.unit
class TestBcryptPasswordHasher:
    """Tests para BcryptPasswordHasher"""
    
    def test_hash_password(self):
        """Test hashear contraseña"""
        hasher = BcryptPasswordHasher()
        password = "testpassword123"
        
        hashed = hasher.hash_password(password)
        
        assert hashed is not None
        assert hashed.startswith("$2b$")
        assert len(hashed) > 50
    
    def test_verify_password_correct(self):
        """Test verificar contraseña correcta"""
        hasher = BcryptPasswordHasher()
        password = "testpassword123"
        
        hashed = hasher.hash_password(password)
        result = hasher.verify_password(password, hashed)
        
        assert result is True
    
    def test_verify_password_incorrect(self):
        """Test verificar contraseña incorrecta"""
        hasher = BcryptPasswordHasher()
        password = "testpassword123"
        wrong_password = "wrongpassword"
        
        hashed = hasher.hash_password(password)
        result = hasher.verify_password(wrong_password, hashed)
        
        assert result is False
    
    def test_hash_password_long_password(self):
        """Test hashear contraseña larga (más de 72 bytes)"""
        hasher = BcryptPasswordHasher()
        # Contraseña de más de 72 bytes
        long_password = "a" * 100
        
        hashed = hasher.hash_password(long_password)
        
        assert hashed is not None
        assert hashed.startswith("$2b$")
        # Verificar que la contraseña truncada funciona
        result = hasher.verify_password(long_password, hashed)
        assert result is True
    
    def test_truncate_password(self):
        """Test truncar contraseña"""
        hasher = BcryptPasswordHasher()
        long_password = "a" * 100
        
        truncated = hasher._truncate_password(long_password)
        
        assert len(truncated.encode('utf-8')) <= 72


@pytest.mark.unit
class TestJWTTokenService:
    """Tests para JWTTokenService"""
    
    def test_create_access_token(self):
        """Test crear token de acceso"""
        service = JWTTokenService(
            secret_key="test_secret_key",
            algorithm="HS256",
            access_token_expire_minutes=30
        )
        
        token = service.create_access_token(
            user_id="user123",
            username="testuser",
            scopes=["read", "write"]
        )
        
        assert token is not None
        assert isinstance(token, str)
        
        # Decodificar y verificar
        payload = jwt.decode(token, "test_secret_key", algorithms=["HS256"])
        assert payload["user_id"] == "user123"
        assert payload["sub"] == "testuser"
        assert payload["scopes"] == ["read", "write"]
        assert payload["type"] == "access"
    
    def test_create_refresh_token(self):
        """Test crear token de refresco"""
        service = JWTTokenService(
            secret_key="test_secret_key",
            algorithm="HS256"
        )
        
        token = service.create_refresh_token(
            user_id="user123",
            username="testuser"
        )
        
        assert token is not None
        assert isinstance(token, str)
        
        # Decodificar y verificar
        payload = jwt.decode(token, "test_secret_key", algorithms=["HS256"])
        assert payload["user_id"] == "user123"
        assert payload["sub"] == "testuser"
        assert payload["type"] == "refresh"
    
    def test_verify_access_token_success(self):
        """Test verificar token de acceso exitoso"""
        service = JWTTokenService(
            secret_key="test_secret_key",
            algorithm="HS256"
        )
        
        token = service.create_access_token(
            user_id="user123",
            username="testuser",
            scopes=["read"]
        )
        
        payload = service.verify_access_token(token)
        
        assert payload["user_id"] == "user123"
        assert payload["sub"] == "testuser"
        assert payload["type"] == "access"
    
    def test_verify_access_token_invalid(self):
        """Test verificar token de acceso inválido"""
        service = JWTTokenService(
            secret_key="test_secret_key",
            algorithm="HS256"
        )
        
        with pytest.raises(ValueError, match="Token inválido"):
            service.verify_access_token("invalid_token")
    
    def test_verify_access_token_wrong_type(self):
        """Test verificar token de acceso con tipo incorrecto"""
        service = JWTTokenService(
            secret_key="test_secret_key",
            algorithm="HS256"
        )
        
        # Crear refresh token pero intentar verificar como access token
        refresh_token = service.create_refresh_token(
            user_id="user123",
            username="testuser"
        )
        
        with pytest.raises(ValueError, match="Token de acceso requerido"):
            service.verify_access_token(refresh_token)
    
    def test_verify_refresh_token_success(self):
        """Test verificar token de refresco exitoso"""
        service = JWTTokenService(
            secret_key="test_secret_key",
            algorithm="HS256"
        )
        
        token = service.create_refresh_token(
            user_id="user123",
            username="testuser"
        )
        
        payload = service.verify_refresh_token(token)
        
        assert payload["user_id"] == "user123"
        assert payload["sub"] == "testuser"
        assert payload["type"] == "refresh"
    
    def test_verify_refresh_token_invalid(self):
        """Test verificar token de refresco inválido"""
        service = JWTTokenService(
            secret_key="test_secret_key",
            algorithm="HS256"
        )
        
        with pytest.raises(ValueError, match="Token inválido"):
            service.verify_refresh_token("invalid_token")
    
    def test_verify_refresh_token_wrong_type(self):
        """Test verificar token de refresco con tipo incorrecto"""
        service = JWTTokenService(
            secret_key="test_secret_key",
            algorithm="HS256"
        )
        
        # Crear access token pero intentar verificar como refresh token
        access_token = service.create_access_token(
            user_id="user123",
            username="testuser",
            scopes=["read"]
        )
        
        with pytest.raises(ValueError, match="Token de refresco requerido"):
            service.verify_refresh_token(access_token)
    
    def test_token_expiration(self):
        """Test expiración de token"""
        service = JWTTokenService(
            secret_key="test_secret_key",
            algorithm="HS256",
            access_token_expire_minutes=1
        )
        
        # Crear token con expiración muy corta
        expire = datetime.utcnow() - timedelta(minutes=2)  # Ya expirado
        to_encode = {
            "sub": "testuser",
            "user_id": "user123",
            "scopes": ["read"],
            "exp": expire,
            "iat": datetime.utcnow() - timedelta(minutes=3),
            "type": "access"
        }
        expired_token = jwt.encode(to_encode, "test_secret_key", algorithm="HS256")
        
        with pytest.raises(ValueError, match="Token expirado"):
            service.verify_access_token(expired_token)

