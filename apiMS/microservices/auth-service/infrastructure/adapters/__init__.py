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

from ...domain.ports import IPasswordHasher, ITokenService


class BcryptPasswordHasher(IPasswordHasher):
    """Adaptador para hashear contraseñas con bcrypt"""
    
    # Bcrypt tiene una limitación de 72 bytes para las contraseñas
    MAX_PASSWORD_BYTES = 72
    
    def __init__(self):
        # Configurar CryptContext para bcrypt
        # Usar 'bcrypt' scheme
        # Nota: passlib valida internamente antes de hashear, por lo que
        # debemos truncar la contraseña ANTES de pasarla a hash()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def _truncate_password(self, password: str) -> str:
        """Trunca la contraseña a 72 bytes de forma segura
        
        Nota: Bcrypt limita las contraseñas a 72 bytes. Para evitar problemas
        con passlib que valida antes de hashear, truncamos siempre si es necesario.
        """
        password_bytes = password.encode('utf-8')
        
        # Truncar a 72 bytes si es necesario
        # Usamos 72 bytes exactos porque ese es el límite de bcrypt
        if len(password_bytes) > self.MAX_PASSWORD_BYTES:
            truncated = password_bytes[:self.MAX_PASSWORD_BYTES]
            return truncated.decode('utf-8', errors='ignore')
        
        return password
    
    def hash_password(self, plain_password: str) -> str:
        """Hashear contraseña
        
        Nota: Bcrypt tiene una limitación de 72 bytes. Si la contraseña
        excede este límite, se trunca automáticamente antes de hashearla.
        """
        # Siempre truncar primero para evitar errores de passlib
        truncated_password = self._truncate_password(plain_password)
        
        try:
            return self.pwd_context.hash(truncated_password)
        except Exception as e:
            # Si aún hay error, intentar truncar más agresivamente
            error_str = str(e).lower()
            if "72" in error_str or "bytes" in error_str or "longer" in error_str:
                # Truncar a 70 bytes para estar seguros
                password_bytes = truncated_password.encode('utf-8')[:70]
                safe_password = password_bytes.decode('utf-8', errors='ignore')
                return self.pwd_context.hash(safe_password)
            raise
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verificar contraseña
        
        Nota: Si la contraseña original fue truncada al registrarse,
        también debe truncarse aquí para verificación.
        """
        # Truncar usando el mismo método que en hash_password
        truncated_password = self._truncate_password(plain_password)
        
        return self.pwd_context.verify(truncated_password, hashed_password)


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

