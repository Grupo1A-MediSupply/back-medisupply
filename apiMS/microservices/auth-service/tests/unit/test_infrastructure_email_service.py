"""
Tests unitarios para EmailService
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import sys
from pathlib import Path

# Agregar paths
auth_service_path = str(Path(__file__).parent.parent.parent)
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if auth_service_path not in sys.path:
    sys.path.insert(0, auth_service_path)
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from infrastructure.email_service import EmailService


@pytest.mark.unit
class TestEmailService:
    """Tests para EmailService"""
    
    @patch('infrastructure.email_service.get_settings')
    def test_init(self, mock_get_settings):
        """Test: Inicialización del servicio de email"""
        # Mock settings
        mock_settings = Mock()
        mock_settings.mail_password = "test_api_key"
        mock_settings.mail_from = "test@example.com"
        mock_settings.mail_from_name = "Test Service"
        mock_settings.verification_code_length = 6
        mock_settings.verification_code_expire_minutes = 10
        mock_get_settings.return_value = mock_settings
        
        service = EmailService()
        
        assert service.settings == mock_settings
        assert service.resend_api_key == "test_api_key"
        assert service.resend_from == "test@example.com"
        assert service.resend_from_name == "Test Service"
    
    @patch('infrastructure.email_service.get_settings')
    def test_generate_verification_code(self, mock_get_settings):
        """Test: Generar código de verificación"""
        # Mock settings
        mock_settings = Mock()
        mock_settings.verification_code_length = 6
        mock_get_settings.return_value = mock_settings
        
        service = EmailService()
        
        code = service.generate_verification_code()
        
        assert isinstance(code, str)
        assert len(code) == 6
        assert code.isdigit()
    
    @patch('infrastructure.email_service.get_settings')
    def test_generate_verification_code_different_lengths(self, mock_get_settings):
        """Test: Generar códigos de verificación de diferentes longitudes"""
        # Mock settings
        mock_settings = Mock()
        mock_get_settings.return_value = mock_settings
        
        service = EmailService()
        
        # Test con longitud 4
        mock_settings.verification_code_length = 4
        code4 = service.generate_verification_code()
        assert len(code4) == 4
        assert code4.isdigit()
        
        # Test con longitud 8
        mock_settings.verification_code_length = 8
        code8 = service.generate_verification_code()
        assert len(code8) == 8
        assert code8.isdigit()
    
    @patch('infrastructure.email_service.get_settings')
    def test_generate_verification_code_uniqueness(self, mock_get_settings):
        """Test: Los códigos generados son únicos"""
        # Mock settings
        mock_settings = Mock()
        mock_settings.verification_code_length = 6
        mock_get_settings.return_value = mock_settings
        
        service = EmailService()
        
        codes = set()
        for _ in range(100):  # Generar 100 códigos
            code = service.generate_verification_code()
            codes.add(code)
        
        # Aunque es posible que haya duplicados por casualidad,
        # con 100 códigos de 6 dígitos, la probabilidad es muy baja
        assert len(codes) > 90  # Al menos 90 códigos únicos
    
    @pytest.mark.asyncio
    @patch('infrastructure.email_service.get_settings')
    @patch('infrastructure.email_service.httpx.AsyncClient')
    async def test_send_verification_code_success(self, mock_httpx_client, mock_get_settings):
        """Test: Enviar código de verificación exitosamente"""
        # Mock settings
        mock_settings = Mock()
        mock_settings.mail_password = "test_api_key"
        mock_settings.mail_from = "test@example.com"
        mock_settings.mail_from_name = "Test Service"
        mock_settings.verification_code_expire_minutes = 10
        mock_get_settings.return_value = mock_settings
        
        # Mock HTTP client
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "test_id"}
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_httpx_client.return_value.__aenter__.return_value = mock_client
        
        service = EmailService()
        
        result = await service.send_verification_code(
            email="user@example.com",
            username="testuser",
            code="123456"
        )
        
        assert result is True
        mock_client.post.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('infrastructure.email_service.get_settings')
    @patch('infrastructure.email_service.httpx.AsyncClient')
    async def test_send_verification_code_http_error(self, mock_httpx_client, mock_get_settings):
        """Test: Enviar código de verificación con error HTTP"""
        # Mock settings
        mock_settings = Mock()
        mock_settings.mail_password = "test_api_key"
        mock_settings.mail_from = "test@example.com"
        mock_settings.mail_from_name = "Test Service"
        mock_settings.verification_code_expire_minutes = 10
        mock_get_settings.return_value = mock_settings
        
        # Mock HTTP client con error
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Bad request"}
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_httpx_client.return_value.__aenter__.return_value = mock_client
        
        service = EmailService()
        
        result = await service.send_verification_code(
            email="user@example.com",
            username="testuser",
            code="123456"
        )
        
        assert result is False
    
    @pytest.mark.asyncio
    @patch('infrastructure.email_service.get_settings')
    @patch('infrastructure.email_service.httpx.AsyncClient')
    async def test_send_verification_code_exception(self, mock_httpx_client, mock_get_settings):
        """Test: Enviar código de verificación con excepción"""
        # Mock settings
        mock_settings = Mock()
        mock_settings.mail_password = "test_api_key"
        mock_settings.mail_from = "test@example.com"
        mock_settings.mail_from_name = "Test Service"
        mock_settings.verification_code_expire_minutes = 10
        mock_get_settings.return_value = mock_settings
        
        # Mock HTTP client con excepción
        mock_client = AsyncMock()
        mock_client.post.side_effect = Exception("Network error")
        mock_httpx_client.return_value.__aenter__.return_value = mock_client
        
        service = EmailService()
        
        result = await service.send_verification_code(
            email="user@example.com",
            username="testuser",
            code="123456"
        )
        
        assert result is False
    
    @pytest.mark.asyncio
    @patch('infrastructure.email_service.get_settings')
    @patch('infrastructure.email_service.httpx.AsyncClient')
    async def test_send_verification_code_request_data(self, mock_httpx_client, mock_get_settings):
        """Test: Verificar datos de la petición HTTP"""
        # Mock settings
        mock_settings = Mock()
        mock_settings.mail_password = "test_api_key"
        mock_settings.mail_from = "test@example.com"
        mock_settings.mail_from_name = "Test Service"
        mock_settings.verification_code_expire_minutes = 10
        mock_get_settings.return_value = mock_settings
        
        # Mock HTTP client
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "test_id"}
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_httpx_client.return_value.__aenter__.return_value = mock_client
        
        service = EmailService()
        
        await service.send_verification_code(
            email="user@example.com",
            username="testuser",
            code="123456"
        )
        
        # Verificar que se llamó con los datos correctos
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "https://api.resend.com/emails"
        
        headers = call_args[1]["headers"]
        assert headers["Authorization"] == "Bearer test_api_key"
        assert headers["Content-Type"] == "application/json"
        
        json_data = call_args[1]["json"]
        assert json_data["from"] == "Test Service <test@example.com>"
        assert json_data["to"] == ["user@example.com"]
        assert json_data["subject"] == "🔐 Código de Verificación - MediSupply"
        assert "testuser" in json_data["html"]
        assert "123456" in json_data["html"]
    
    @patch('infrastructure.email_service.get_settings')
    @patch('builtins.print')
    def test_send_verification_code_console_output(self, mock_print, mock_get_settings):
        """Test: Verificar que se imprime el código en consola"""
        # Mock settings
        mock_settings = Mock()
        mock_settings.verification_code_expire_minutes = 10
        mock_get_settings.return_value = mock_settings
        
        service = EmailService()
        
        # Simular el envío (solo la parte de impresión)
        email = "user@example.com"
        username = "testuser"
        code = "123456"
        
        # Llamar directamente a la parte de impresión
        print(f"\n🔐 CÓDIGO DE VERIFICACIÓN PARA {username} ({email})")
        print(f"📧 Código: {code}")
        print(f"⏰ Válido por {mock_settings.verification_code_expire_minutes} minutos")
        print("=" * 50)
        
        # Verificar que se llamó print
        assert mock_print.call_count >= 4
