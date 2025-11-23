"""Servicio de envío de emails"""
import random
import string

import httpx
try:
    from ..config import get_settings
except ImportError:
    from infrastructure.config import get_settings


class EmailService:
    """Servicio para envío de emails"""
    
    def __init__(self):
        self.settings = get_settings()
        self.simulate = getattr(self.settings, "mail_simulate", False)
        # Configurar para Resend API
        self.resend_api_key = self.settings.mail_password  # Usar mail_password como API key
        self.resend_from = self.settings.mail_from
        self.resend_from_name = self.settings.mail_from_name
    
    def generate_verification_code(self) -> str:
        """Generar código de verificación de 6 dígitos"""
        return ''.join(random.choices(string.digits, k=self.settings.verification_code_length))
    
    async def send_verification_code(self, email: str, username: str, code: str) -> bool:
        """Enviar código de verificación por email usando Resend API"""
        try:
            # Siempre imprimir el código en consola para debug
            print(f"\n🔐 CÓDIGO DE VERIFICACIÓN PARA {username} ({email})")
            print(f"📧 Código: {code}")
            print(f"⏰ Válido por {self.settings.verification_code_expire_minutes} minutos")
            print("=" * 50)

            if self.simulate:
                print("🧪 Simulación de envío activada (MAIL_SIMULATE=True). No se realiza solicitud HTTP.")
                return True

            if not self.resend_api_key:
                print("⚠️ Resend API key no configurada. Configura MAIL_PASSWORD o activa MAIL_SIMULATE.")
                return False
            
            # Enviar por email usando Resend API
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
                    <h2 style="color: #2c3e50; text-align: center;">🔐 Código de Verificación</h2>
                    
                    <p>Hola <strong>{username}</strong>,</p>
                    
                    <p>Has iniciado sesión en tu cuenta de MediSupply. Para completar el proceso, 
                    utiliza el siguiente código de verificación:</p>
                    
                    <div style="background-color: #ffffff; padding: 20px; text-align: center; 
                                border-radius: 8px; margin: 20px 0;">
                        <h1 style="color: #3498db; font-size: 32px; letter-spacing: 5px; 
                                  margin: 0; font-family: 'Courier New', monospace;">
                            {code}
                        </h1>
                    </div>
                    
                    <p><strong>⏰ Este código expira en {self.settings.verification_code_expire_minutes} minutos.</strong></p>
                    
                    <p>Si no has iniciado sesión, por favor ignora este email.</p>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                    
                    <p style="color: #7f8c8d; font-size: 12px; text-align: center;">
                        Este es un email automático, por favor no respondas.
                    </p>
                </div>
            </body>
            </html>
            """
            
            # Usar Resend API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {self.resend_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "from": f"{self.resend_from_name} <{self.resend_from}>",
                        "to": [email],
                        "subject": "🔐 Código de Verificación - MediSupply",
                        "html": html_content
                    }
                )
                
                if 200 <= response.status_code < 300:
                    print(f"✅ Email enviado exitosamente a {email} via Resend")
                    return True
                else:
                    print(f"❌ Error enviando email via Resend: {response.status_code} - {response.text}")
                    return False
            
        except Exception as e:
            print(f"❌ Error enviando email: {e}")
            return False
    
    async def send_welcome_email(self, email: str, username: str) -> bool:
        """Enviar email de bienvenida"""
        try:
            if self.simulate:
                print(f"\n🎉 Email de bienvenida simulado para {username} ({email})")
                return True
            if not self.resend_api_key:
                print("⚠️ Resend API key no configurada. Configura MAIL_PASSWORD o activa MAIL_SIMULATE.")
                return False

            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
                    <h2 style="color: #2c3e50; text-align: center;">🎉 ¡Bienvenido a MediSupply!</h2>
                    
                    <p>Hola <strong>{username}</strong>,</p>
                    
                    <p>¡Gracias por registrarte en MediSupply! Tu cuenta ha sido creada exitosamente.</p>
                    
                    <p>Ahora puedes:</p>
                    <ul>
                        <li>Iniciar sesión en tu cuenta</li>
                        <li>Gestionar tu perfil</li>
                        <li>Acceder a todos nuestros servicios</li>
                    </ul>
                    
                    <p>Si tienes alguna pregunta, no dudes en contactarnos.</p>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                    
                    <p style="color: #7f8c8d; font-size: 12px; text-align: center;">
                        MediSupply - Sistema de Gestión Médica
                    </p>
                </div>
            </body>
            </html>
            """

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {self.resend_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "from": f"{self.resend_from_name} <{self.resend_from}>",
                        "to": [email],
                        "subject": "🎉 ¡Bienvenido a MediSupply!",
                        "html": html_content
                    }
                )

            if 200 <= response.status_code < 300:
                print(f"✅ Email de bienvenida enviado exitosamente a {email} via Resend")
                return True

            print(f"❌ Error enviando email de bienvenida via Resend: {response.status_code} - {response.text}")
            return False
            
        except Exception as e:
            print(f"Error enviando email de bienvenida: {e}")
            return False


# Instancia global del servicio de email
email_service = EmailService()
