"""
Handlers para comandos y queries
"""
from typing import Optional
from uuid import uuid4
import sys
from pathlib import Path

# Agregar el path del módulo shared al PYTHONPATH
shared_path = str(Path(__file__).parent.parent.parent.parent / "shared")
if shared_path not in sys.path:
    sys.path.insert(0, shared_path)

from shared.domain.value_objects import EntityId, Email
from shared.domain.events import event_bus
try:
    from ..commands import (
        RegisterUserCommand, LoginCommand, RefreshTokenCommand,
        ChangePasswordCommand, DeactivateUserCommand, UpdateProfileCommand,
        VerifyCodeCommand
    )
    from ..queries import (
        GetUserByIdQuery, GetUserByUsernameQuery, GetUserByEmailQuery,
        VerifyTokenQuery, GetCurrentUserQuery
    )
    from ...domain.entities import User
    from ...domain.value_objects import Username, HashedPassword, FullName, PhoneNumber
    from ...domain.ports import IUserRepository, IPasswordHasher, ITokenService
    from ...domain.events import TokenRefreshedEvent
except ImportError:
    from application.commands import (
        RegisterUserCommand, LoginCommand, RefreshTokenCommand,
        ChangePasswordCommand, DeactivateUserCommand, UpdateProfileCommand,
        VerifyCodeCommand
    )
    from application.queries import (
        GetUserByIdQuery, GetUserByUsernameQuery, GetUserByEmailQuery,
        VerifyTokenQuery, GetCurrentUserQuery
    )
    from domain.entities import User
    from domain.value_objects import Username, HashedPassword, FullName, PhoneNumber
    from domain.ports import IUserRepository, IPasswordHasher, ITokenService
    from domain.events import TokenRefreshedEvent


class RegisterUserCommandHandler:
    """Handler para el comando RegisterUser"""
    
    def __init__(
        self,
        user_repository: IUserRepository,
        password_hasher: IPasswordHasher
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher
    
    async def handle(self, command: RegisterUserCommand) -> User:
        """Manejar comando de registro de usuario"""
        # Validar confirmación de contraseña
        if command.password != command.confirm_password:
            raise ValueError("Las contraseñas no coinciden")
        
        # Validar que no exista el usuario
        username = Username(command.username)
        email = Email(command.email)
        
        if await self.user_repository.exists_by_username(username):
            raise ValueError(f"El username '{command.username}' ya está registrado")
        
        if await self.user_repository.exists_by_email(email):
            raise ValueError(f"El email '{command.email}' ya está registrado")
        
        # Hashear contraseña (el password_hasher maneja el truncamiento automático)
        # El BcryptPasswordHasher ya trunca automáticamente antes de hashear
        hashed_password = HashedPassword(
            self.password_hasher.hash_password(command.password)
        )
        
        # Crear usuario
        user = User.register(
            user_id=EntityId(str(uuid4())),
            email=email,
            username=username,
            hashed_password=hashed_password,
            full_name=FullName(command.full_name) if command.full_name else None,
            phone_number=PhoneNumber(command.phone_number) if command.phone_number else None,
            is_active=command.is_active,
            is_superuser=command.is_superuser
        )
        
        # Guardar usuario
        user = await self.user_repository.save(user)
        
        # Publicar eventos de dominio
        for event in user.get_domain_events():
            await event_bus.publish(event)
        
        user.clear_domain_events()
        
        return user


class LoginCommandHandler:
    """Handler para el comando Login"""
    
    def __init__(
        self,
        user_repository: IUserRepository,
        password_hasher: IPasswordHasher,
        verification_code_repository,
        email_service
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.verification_code_repository = verification_code_repository
        self.email_service = email_service
    
    async def handle(self, command: LoginCommand) -> dict:
        """Manejar comando de login"""
        try:
            # Buscar usuario por username o email
            username = Username(command.username)
            user = await self.user_repository.find_by_username(username)
            
            if not user:
                # Intentar con email
                try:
                    email = Email(command.username)
                    user = await self.user_repository.find_by_email(email)
                except ValueError:
                    pass
            
            if not user:
                raise ValueError("Credenciales incorrectas")
            
            # Verificar contraseña
            if not self.password_hasher.verify_password(
                command.password,
                str(user.hashed_password)
            ):
                raise ValueError("Credenciales incorrectas")
            
            # Verificar que el usuario esté activo
            if not user.is_active:
                raise ValueError("Usuario desactivado")
            
            # Registrar evento de login
            user.login()
            
            # Publicar eventos
            for event in user.get_domain_events():
                await event_bus.publish(event)
            
            user.clear_domain_events()
            
            # Generar código de verificación
            verification_code = self.email_service.generate_verification_code()
            
            # Guardar código en la base de datos
            verification_code_model = await self.verification_code_repository.create_verification_code(
                user_id=str(user.id),
                email=str(user.email),
                code=verification_code
            )
            
            # Enviar código por email
            email_sent = await self.email_service.send_verification_code(
                email=str(user.email),
                username=str(user.username),
                code=verification_code
            )
            
            if not email_sent:
                raise ValueError("Error enviando código de verificación")
            
            # Hacer commit de la transacción
            self.verification_code_repository.db.commit()
            
            return {
                "message": "Código de verificación enviado al email",
                "user_id": str(user.id),
                "email": str(user.email),
                "requires_verification": True
            }
        except Exception as e:
            print(f"Error en LoginCommandHandler: {e}")
            raise


class RefreshTokenCommandHandler:
    """Handler para el comando RefreshToken"""
    
    def __init__(
        self,
        user_repository: IUserRepository,
        token_service: ITokenService
    ):
        self.user_repository = user_repository
        self.token_service = token_service
    
    async def handle(self, command: RefreshTokenCommand) -> dict:
        """Manejar comando de refresh token"""
        # Verificar refresh token
        payload = self.token_service.verify_refresh_token(command.refresh_token)
        
        user_id = payload.get("user_id")
        if not user_id:
            raise ValueError("Token inválido")
        
        # Buscar usuario
        user = await self.user_repository.find_by_id(EntityId(user_id))
        if not user or not user.is_active:
            raise ValueError("Usuario no encontrado o inactivo")
        
        # Publicar evento
        event = TokenRefreshedEvent(user_id)
        await event_bus.publish(event)
        
        # Crear nuevos tokens
        access_token = self.token_service.create_access_token(
            user_id=str(user.id),
            username=str(user.username),
            scopes=["read", "write"]
        )
        
        new_refresh_token = self.token_service.create_refresh_token(
            user_id=str(user.id),
            username=str(user.username)
        )
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }


class ChangePasswordCommandHandler:
    """Handler para el comando ChangePassword"""
    
    def __init__(
        self,
        user_repository: IUserRepository,
        password_hasher: IPasswordHasher
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher
    
    async def handle(self, command: ChangePasswordCommand) -> User:
        """Manejar comando de cambio de contraseña"""
        # Buscar usuario
        user = await self.user_repository.find_by_id(EntityId(command.user_id))
        if not user:
            raise ValueError("Usuario no encontrado")
        
        # Verificar contraseña actual
        if not self.password_hasher.verify_password(
            command.old_password,
            str(user.hashed_password)
        ):
            raise ValueError("Contraseña actual incorrecta")
        
        # Cambiar contraseña
        new_hashed_password = HashedPassword(
            self.password_hasher.hash_password(command.new_password)
        )
        user.change_password(new_hashed_password)
        
        # Guardar usuario
        user = await self.user_repository.save(user)
        
        return user


class DeactivateUserCommandHandler:
    """Handler para el comando DeactivateUser"""
    
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
    
    async def handle(self, command: DeactivateUserCommand) -> User:
        """Manejar comando de desactivación de usuario"""
        # Buscar usuario
        user = await self.user_repository.find_by_id(EntityId(command.user_id))
        if not user:
            raise ValueError("Usuario no encontrado")
        
        # Desactivar usuario
        user.deactivate()
        
        # Guardar usuario
        user = await self.user_repository.save(user)
        
        # Publicar eventos
        for event in user.get_domain_events():
            await event_bus.publish(event)
        
        user.clear_domain_events()
        
        return user


class UpdateProfileCommandHandler:
    """Handler para el comando UpdateProfile"""
    
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
    
    async def handle(self, command: UpdateProfileCommand) -> User:
        """Manejar comando de actualización de perfil"""
        # Buscar usuario
        user = await self.user_repository.find_by_id(EntityId(command.user_id))
        if not user:
            raise ValueError("Usuario no encontrado")
        
        # Actualizar perfil
        full_name = FullName(command.full_name) if command.full_name else None
        phone_number = PhoneNumber(command.phone_number) if command.phone_number else None
        user.update_profile(full_name=full_name, phone_number=phone_number)
        
        # Guardar usuario
        user = await self.user_repository.save(user)
        
        return user


# ========== Query Handlers ==========

class GetUserByIdQueryHandler:
    """Handler para la query GetUserById"""
    
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
    
    async def handle(self, query: GetUserByIdQuery) -> Optional[User]:
        """Manejar query de obtener usuario por ID"""
        return await self.user_repository.find_by_id(EntityId(query.user_id))


class GetUserByUsernameQueryHandler:
    """Handler para la query GetUserByUsername"""
    
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
    
    async def handle(self, query: GetUserByUsernameQuery) -> Optional[User]:
        """Manejar query de obtener usuario por username"""
        return await self.user_repository.find_by_username(Username(query.username))


class GetUserByEmailQueryHandler:
    """Handler para la query GetUserByEmail"""
    
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
    
    async def handle(self, query: GetUserByEmailQuery) -> Optional[User]:
        """Manejar query de obtener usuario por email"""
        return await self.user_repository.find_by_email(Email(query.email))


class GetCurrentUserQueryHandler:
    """Handler para la query GetCurrentUser"""
    
    def __init__(
        self,
        user_repository: IUserRepository,
        token_service: ITokenService
    ):
        self.user_repository = user_repository
        self.token_service = token_service
    
    async def handle(self, query: GetCurrentUserQuery) -> Optional[User]:
        """Manejar query de obtener usuario actual desde token"""
        # Verificar token
        payload = self.token_service.verify_access_token(query.token)
        
        user_id = payload.get("user_id")
        if not user_id:
            raise ValueError("Token inválido")
        
        # Buscar usuario
        return await self.user_repository.find_by_id(EntityId(user_id))


class VerifyTokenQueryHandler:
    """Handler para la query VerifyToken"""
    
    def __init__(self, token_service: ITokenService):
        self.token_service = token_service
    
    async def handle(self, query: VerifyTokenQuery) -> dict:
        """Manejar query de verificación de token"""
        try:
            payload = self.token_service.verify_access_token(query.token)
            return {
                "valid": True,
                "payload": payload
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }


class VerifyCodeCommandHandler:
    """Handler para el comando VerifyCode"""
    
    def __init__(
        self,
        verification_code_repository,
        token_service: ITokenService
    ):
        self.verification_code_repository = verification_code_repository
        self.token_service = token_service
    
    async def handle(self, command: VerifyCodeCommand) -> dict:
        """Manejar comando de verificación de código"""
        # Buscar código válido
        verification_code = await self.verification_code_repository.get_valid_code(
            command.user_id, command.code
        )
        
        if not verification_code:
            raise ValueError("Código inválido o expirado")
        
        # Marcar código como usado
        await self.verification_code_repository.mark_code_as_used(verification_code)
        
        # Generar tokens de acceso
        access_token = self.token_service.create_access_token(
            user_id=verification_code.user_id,
            username="",  # No tenemos username aquí, se puede obtener del usuario si es necesario
            scopes=["read", "write"]
        )
        
        refresh_token = self.token_service.create_refresh_token(
            user_id=verification_code.user_id,
            username=""  # No tenemos username aquí, se puede obtener del usuario si es necesario
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

