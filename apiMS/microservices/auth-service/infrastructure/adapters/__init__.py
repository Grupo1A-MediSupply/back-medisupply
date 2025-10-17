"""
Adaptadores de infraestructura
"""
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
import sys
from pathlib import Path

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

try:
    from ...domain.ports import IPasswordHasher, ITokenService
except ImportError:
    from domain.ports import IPasswordHasher, ITokenService


class BcryptPasswordHasher(IPasswordHasher):
    """Adaptador para hashear contraseñas con bcrypt"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def hash_password(self, plain_password: str) -> str:
        """Hashear contraseña"""
        # Truncar contraseña a 72 bytes máximo para compatibilidad con bcrypt
        if len(plain_password.encode('utf-8')) > 72:
            # Truncar a 72 bytes, no caracteres
            password_bytes = plain_password.encode('utf-8')[:72]
            plain_password = password_bytes.decode('utf-8', errors='ignore')
        return self.pwd_context.hash(plain_password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verificar contraseña"""
        # Truncar contraseña a 72 bytes máximo para compatibilidad con bcrypt
        if len(plain_password.encode('utf-8')) > 72:
            # Truncar a 72 bytes, no caracteres
            password_bytes = plain_password.encode('utf-8')[:72]
            plain_password = password_bytes.decode('utf-8', errors='ignore')
        return self.pwd_context.verify(plain_password, hashed_password)


class JWTTokenService(ITokenService):
    """Adaptador para tokens JWT"""
    
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
    
    def create_access_token(self, user_id: str, username: str, scopes: list) -> str:
        """Crear token de acceso"""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode = {
            "sub": username,
            "user_id": user_id,
            "scopes": scopes,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: str, username: str) -> str:
        """Crear token de refresco"""
        expire = datetime.utcnow() + timedelta(days=7)
        
        to_encode = {
            "sub": username,
            "user_id": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_access_token(self, token: str) -> dict:
        """Verificar token de acceso"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            if payload.get("type") != "access":
                raise ValueError("Token de acceso requerido")
            
            return payload
            
        except ExpiredSignatureError:
            raise ValueError("Token expirado")
        except InvalidTokenError:
            raise ValueError("Token inválido")
    
    def verify_refresh_token(self, token: str) -> dict:
        """Verificar token de refresco"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            if payload.get("type") != "refresh":
                raise ValueError("Token de refresco requerido")
            
            return payload
            
        except ExpiredSignatureError:
            raise ValueError("Token expirado")
        except InvalidTokenError:
            raise ValueError("Token inválido")

