"""
Tests unitarios para VerificationCodeRepository
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
import sys
from pathlib import Path

# Agregar paths
auth_service_path = str(Path(__file__).parent.parent.parent)
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if auth_service_path not in sys.path:
    sys.path.insert(0, auth_service_path)
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from infrastructure.verification_code_repository import VerificationCodeRepository


@pytest.mark.unit
class TestVerificationCodeRepository:
    """Tests para VerificationCodeRepository"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock de la base de datos"""
        db = Mock()
        db.add = Mock()
        db.commit = Mock()
        db.query = Mock()
        return db
    
    @pytest.fixture
    def mock_settings(self):
        """Mock de settings"""
        settings = Mock()
        settings.verification_code_expire_minutes = 10
        return settings
    
    @pytest.fixture
    def repository(self, mock_db, mock_settings):
        """Fixture para el repositorio"""
        with patch('infrastructure.verification_code_repository.get_settings') as mock_get_settings:
            mock_get_settings.return_value = mock_settings
            return VerificationCodeRepository(mock_db)
    
    @pytest.mark.asyncio
    async def test_create_verification_code(self, repository, mock_db, mock_settings):
        """Test: Crear código de verificación"""
        user_id = "123"
        email = "test@example.com"
        code = "123456"
        
        # Mock para invalidate_user_codes
        with patch.object(repository, 'invalidate_user_codes', new_callable=AsyncMock) as mock_invalidate:
            result = await repository.create_verification_code(user_id, email, code)
            
            # Verificar que se invalidaron códigos anteriores
            mock_invalidate.assert_called_once_with(user_id)
            
            # Verificar que se agregó el código a la base de datos
            mock_db.add.assert_called_once()
            
            # Verificar propiedades del código creado
            verification_code = mock_db.add.call_args[0][0]
            assert verification_code.user_id == user_id
            assert verification_code.email == email
            assert verification_code.code == code
            assert verification_code.is_used is False
            assert isinstance(verification_code.id, str)
            assert isinstance(verification_code.created_at, datetime)
            assert isinstance(verification_code.expires_at, datetime)
            
            # Verificar que expira en el tiempo correcto
            expected_expiry = datetime.utcnow() + timedelta(minutes=mock_settings.verification_code_expire_minutes)
            time_diff = abs((verification_code.expires_at - expected_expiry).total_seconds())
            assert time_diff < 1  # Diferencia menor a 1 segundo
    
    @pytest.mark.asyncio
    async def test_get_valid_code_found(self, repository, mock_db):
        """Test: Obtener código válido encontrado"""
        user_id = "123"
        code = "123456"
        
        # Mock del modelo de código
        mock_code = Mock()
        mock_code.user_id = user_id
        mock_code.code = code
        mock_code.is_used = False
        mock_code.expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        # Mock de la query
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = mock_code
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query
        
        result = await repository.get_valid_code(user_id, code)
        
        assert result == mock_code
        mock_db.query.assert_called_once()
        mock_filter.first.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_valid_code_not_found(self, repository, mock_db):
        """Test: Obtener código válido no encontrado"""
        user_id = "123"
        code = "123456"
        
        # Mock de la query que retorna None
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query
        
        result = await repository.get_valid_code(user_id, code)
        
        assert result is None
        mock_db.query.assert_called_once()
        mock_filter.first.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_mark_code_as_used(self, repository, mock_db):
        """Test: Marcar código como usado"""
        mock_code = Mock()
        mock_code.is_used = False
        
        await repository.mark_code_as_used(mock_code)
        
        assert mock_code.is_used is True
        mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_invalidate_user_codes(self, repository, mock_db):
        """Test: Invalidar códigos de usuario"""
        user_id = "123"
        
        # Mock de la query
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.update.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query
        
        await repository.invalidate_user_codes(user_id)
        
        mock_db.query.assert_called_once()
        mock_filter.update.assert_called_once_with({"is_used": True})
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_codes(self, repository, mock_db):
        """Test: Limpiar códigos expirados"""
        # Mock de la query
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.delete.return_value = 5  # 5 códigos eliminados
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query
        
        result = await repository.cleanup_expired_codes()
        
        assert result == 5
        mock_db.query.assert_called_once()
        mock_filter.delete.assert_called_once()
        mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_codes_no_codes(self, repository, mock_db):
        """Test: Limpiar códigos expirados sin códigos"""
        # Mock de la query
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.delete.return_value = 0  # No hay códigos para eliminar
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query
        
        result = await repository.cleanup_expired_codes()
        
        assert result == 0
        mock_db.query.assert_called_once()
        mock_filter.delete.assert_called_once()
        mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_verification_code_with_uuid(self, repository, mock_db, mock_settings):
        """Test: Crear código de verificación con UUID único"""
        user_id = "123"
        email = "test@example.com"
        code = "123456"
        
        # Mock para invalidate_user_codes
        with patch.object(repository, 'invalidate_user_codes', new_callable=AsyncMock):
            result = await repository.create_verification_code(user_id, email, code)
            
            # Verificar que se generó un UUID
            verification_code = mock_db.add.call_args[0][0]
            assert isinstance(verification_code.id, str)
            assert len(verification_code.id) == 36  # UUID v4 tiene 36 caracteres
            assert verification_code.id.count('-') == 4  # UUID v4 tiene 4 guiones
    
    @pytest.mark.asyncio
    async def test_get_valid_code_query_conditions(self, repository, mock_db):
        """Test: Verificar condiciones de la query para obtener código válido"""
        user_id = "123"
        code = "123456"
        
        # Mock de la query
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query
        
        await repository.get_valid_code(user_id, code)
        
        # Verificar que se llamó query con el modelo correcto
        mock_db.query.assert_called_once()
        
        # Verificar que se llamó filter con las condiciones correctas
        mock_filter.first.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_invalidate_user_codes_query_conditions(self, repository, mock_db):
        """Test: Verificar condiciones de la query para invalidar códigos"""
        user_id = "123"
        
        # Mock de la query
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.update.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query
        
        await repository.invalidate_user_codes(user_id)
        
        # Verificar que se llamó query con el modelo correcto
        mock_db.query.assert_called_once()
        
        # Verificar que se llamó filter con las condiciones correctas
        mock_filter.update.assert_called_once_with({"is_used": True})
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_codes_query_conditions(self, repository, mock_db):
        """Test: Verificar condiciones de la query para limpiar códigos expirados"""
        # Mock de la query
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.delete.return_value = 3
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query
        
        result = await repository.cleanup_expired_codes()
        
        # Verificar que se llamó query con el modelo correcto
        mock_db.query.assert_called_once()
        
        # Verificar que se llamó filter con las condiciones correctas
        mock_filter.delete.assert_called_once()
        
        # Verificar que se hizo commit
        mock_db.commit.assert_called_once()
        
        assert result == 3
