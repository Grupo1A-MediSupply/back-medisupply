"""
Repositorio para códigos de verificación
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from .repositories import VerificationCodeModel
try:
    from ..config import get_settings
except ImportError:
    from infrastructure.config import get_settings
import uuid


class VerificationCodeRepository:
    """Repositorio para manejo de códigos de verificación"""
    
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
    
    async def create_verification_code(self, user_id: str, email: str, code: str) -> VerificationCodeModel:
        """Crear un nuevo código de verificación"""
        # Invalidar códigos anteriores del usuario
        await self.invalidate_user_codes(user_id)
        
        # Crear nuevo código
        expires_at = datetime.utcnow() + timedelta(minutes=self.settings.verification_code_expire_minutes)
        
        verification_code = VerificationCodeModel(
            id=str(uuid.uuid4()),
            user_id=user_id,
            code=code,
            email=email,
            expires_at=expires_at,
            is_used=False,
            created_at=datetime.utcnow()
        )
        
        self.db.add(verification_code)
        # No hacer commit aquí, dejar que el handler maneje la transacción
        
        return verification_code
    
    async def get_valid_code(self, user_id: str, code: str) -> Optional[VerificationCodeModel]:
        """Obtener un código válido para un usuario"""
        now = datetime.utcnow()
        
        verification_code = self.db.query(VerificationCodeModel).filter(
            and_(
                VerificationCodeModel.user_id == user_id,
                VerificationCodeModel.code == code,
                VerificationCodeModel.expires_at > now,
                VerificationCodeModel.is_used == False
            )
        ).first()
        
        return verification_code
    
    async def mark_code_as_used(self, verification_code: VerificationCodeModel) -> None:
        """Marcar un código como usado"""
        verification_code.is_used = True
        self.db.commit()
    
    async def invalidate_user_codes(self, user_id: str) -> None:
        """Invalidar todos los códigos de un usuario"""
        self.db.query(VerificationCodeModel).filter(
            VerificationCodeModel.user_id == user_id
        ).update({"is_used": True})
        # No hacer commit aquí, dejar que el handler maneje la transacción
    
    async def cleanup_expired_codes(self) -> int:
        """Limpiar códigos expirados"""
        now = datetime.utcnow()
        deleted_count = self.db.query(VerificationCodeModel).filter(
            VerificationCodeModel.expires_at < now
        ).delete()
        self.db.commit()
        return deleted_count
    
    async def get_latest_code(self, user_id: str) -> Optional[VerificationCodeModel]:
        """Obtener el código más reciente de un usuario (válido o no)"""
        verification_code = self.db.query(VerificationCodeModel).filter(
            VerificationCodeModel.user_id == user_id
        ).order_by(VerificationCodeModel.created_at.desc()).first()
        
        return verification_code