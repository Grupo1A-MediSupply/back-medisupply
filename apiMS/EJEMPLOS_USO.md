# Ejemplos de Uso - API de Autenticación

Este documento contiene ejemplos prácticos de cómo usar cada endpoint de la API.

## URLs Base

- **Servidor**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Endpoints Disponibles

### 1. POST /api/v1/auth/register - Registrar Usuario

Registra un nuevo usuario en el sistema.

**Ejemplo con cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "myuser",
    "password": "password123",
    "full_name": "My User Name"
  }'
```

**Respuesta exitosa (201):**
```json
{
  "id": "372efc13-bf09-43b3-9752-bc5ba6baff5b",
  "email": "user@example.com",
  "username": "myuser",
  "full_name": "My User Name",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-10-10T03:30:23.973908",
  "updated_at": "2025-10-10T03:30:23.973908"
}
```

**Errores posibles:**
- `400`: Usuario o email ya registrado
- `500`: Error interno del servidor

---

### 2. POST /api/v1/auth/login - Iniciar Sesión

Inicia sesión y obtiene tokens de acceso.

**Ejemplo con cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "myuser",
    "password": "password123"
  }'
```

**Nota:** El campo `username` puede ser tanto el nombre de usuario como el email.

**Respuesta exitosa (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Errores posibles:**
- `401`: Credenciales incorrectas
- `500`: Error interno del servidor

**Guardar el token:**
```bash
# En bash
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "myuser", "password": "password123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
```

---

### 3. GET /api/v1/auth/me - Obtener Perfil

Obtiene el perfil del usuario autenticado.

**Ejemplo con cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Respuesta exitosa (200):**
```json
{
  "id": "372efc13-bf09-43b3-9752-bc5ba6baff5b",
  "email": "user@example.com",
  "username": "myuser",
  "full_name": "My User Name",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-10-10T03:30:23.973908",
  "updated_at": "2025-10-10T03:30:23.973908"
}
```

**Errores posibles:**
- `401`: Token inválido o expirado
- `500`: Error interno del servidor

---

### 4. POST /api/v1/auth/refresh - Renovar Token

Refresca el token de acceso usando el refresh token.

**Ejemplo con cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

**Respuesta exitosa (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Errores posibles:**
- `401`: Refresh token inválido o expirado
- `500`: Error interno del servidor

---

### 5. GET /api/v1/auth/verify - Verificar Token

Verifica si un token es válido.

**Ejemplo con cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/auth/verify" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Respuesta exitosa (200):**
```json
{
  "valid": true,
  "user": {
    "id": "372efc13-bf09-43b3-9752-bc5ba6baff5b",
    "username": "myuser",
    "email": "user@example.com"
  },
  "error": null
}
```

**Respuesta con token inválido (200):**
```json
{
  "valid": false,
  "user": null,
  "error": "Token inválido"
}
```

---

### 6. POST /api/v1/auth/logout - Cerrar Sesión

Cierra la sesión del usuario (invalidar tokens).

**Ejemplo con cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/logout" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Respuesta exitosa (200):**
```json
{
  "message": "Sesión cerrada exitosamente"
}
```

**Nota:** En la implementación actual, este endpoint simplemente confirma el logout. En producción, aquí se debería agregar el token a una blacklist (por ejemplo en Redis).

---

## Flujo Completo de Autenticación

### Script de Prueba Completo

```bash
#!/bin/bash

API_URL="http://localhost:8000/api/v1"

echo "=== 1. REGISTRAR USUARIO ==="
curl -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "username": "demouser",
    "password": "demo123456",
    "full_name": "Demo User"
  }' | python3 -m json.tool

echo -e "\n\n=== 2. LOGIN ==="
RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demouser",
    "password": "demo123456"
  }')

echo $RESPONSE | python3 -m json.tool

# Extraer tokens
ACCESS_TOKEN=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
REFRESH_TOKEN=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['refresh_token'])")

echo -e "\n\n=== 3. OBTENER PERFIL ==="
curl -s -X GET "$API_URL/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool

echo -e "\n\n=== 4. VERIFICAR TOKEN ==="
curl -s -X GET "$API_URL/auth/verify" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool

echo -e "\n\n=== 5. REFRESH TOKEN ==="
curl -s -X POST "$API_URL/auth/refresh" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}" | python3 -m json.tool | head -5

echo -e "\n\n=== 6. LOGOUT ==="
curl -s -X POST "$API_URL/auth/logout" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool

echo -e "\n\n✅ PRUEBAS COMPLETADAS"
```

Guarda este script como `test_api.sh`, dale permisos de ejecución y ejecútalo:

```bash
chmod +x test_api.sh
./test_api.sh
```

---

## Usando Python

### Ejemplo con requests

```python
import requests

API_URL = "http://localhost:8000/api/v1"

# 1. Registrar usuario
register_data = {
    "email": "python@example.com",
    "username": "pythonuser",
    "password": "python123",
    "full_name": "Python User"
}
response = requests.post(f"{API_URL}/auth/register", json=register_data)
print("Registro:", response.json())

# 2. Login
login_data = {
    "username": "pythonuser",
    "password": "python123"
}
response = requests.post(f"{API_URL}/auth/login", json=login_data)
tokens = response.json()
access_token = tokens["access_token"]
refresh_token = tokens["refresh_token"]
print("Login exitoso. Token obtenido.")

# 3. Obtener perfil
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(f"{API_URL}/auth/me", headers=headers)
print("Perfil:", response.json())

# 4. Verificar token
response = requests.get(f"{API_URL}/auth/verify", headers=headers)
print("Verificación:", response.json())

# 5. Refresh token
refresh_data = {"refresh_token": refresh_token}
response = requests.post(f"{API_URL}/auth/refresh", json=refresh_data)
new_tokens = response.json()
print("Nuevo access token obtenido")

# 6. Logout
response = requests.post(f"{API_URL}/auth/logout", headers=headers)
print("Logout:", response.json())
```

---

## Usando JavaScript/Fetch

```javascript
const API_URL = 'http://localhost:8000/api/v1';

// 1. Registrar usuario
async function register() {
  const response = await fetch(`${API_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: 'js@example.com',
      username: 'jsuser',
      password: 'javascript123',
      full_name: 'JS User'
    })
  });
  return await response.json();
}

// 2. Login
async function login() {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: 'jsuser',
      password: 'javascript123'
    })
  });
  const data = await response.json();
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
  return data;
}

// 3. Obtener perfil
async function getProfile() {
  const token = localStorage.getItem('access_token');
  const response = await fetch(`${API_URL}/auth/me`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return await response.json();
}

// 4. Verificar token
async function verifyToken() {
  const token = localStorage.getItem('access_token');
  const response = await fetch(`${API_URL}/auth/verify`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return await response.json();
}

// 5. Refresh token
async function refreshToken() {
  const refresh = localStorage.getItem('refresh_token');
  const response = await fetch(`${API_URL}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refresh })
  });
  const data = await response.json();
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
  return data;
}

// 6. Logout
async function logout() {
  const token = localStorage.getItem('access_token');
  const response = await fetch(`${API_URL}/auth/logout`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  });
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  return await response.json();
}
```

---

## Notas Importantes

### Seguridad

1. **En Producción:**
   - Cambia el `SECRET_KEY` en `.env` por una clave segura
   - Usa HTTPS en lugar de HTTP
   - Configura CORS apropiadamente
   - Implementa rate limiting
   - Agrega validación adicional

2. **Tokens:**
   - Access token expira en 30 minutos (configurable)
   - Refresh token expira en 7 días
   - Almacena los tokens de forma segura (nunca en el código fuente)

3. **Contraseñas:**
   - Mínimo 8 caracteres
   - Se hashean con bcrypt antes de almacenarse
   - Nunca se devuelven en las respuestas

### Documentación Interactiva

La mejor forma de probar la API es usando Swagger UI:

1. Abre http://localhost:8000/docs
2. Usa el botón "Try it out" en cada endpoint
3. Para endpoints protegidos:
   - Haz login primero
   - Copia el access_token
   - Click en "Authorize" (candado verde arriba)
   - Pega el token: `Bearer YOUR_TOKEN`
   - Ahora puedes usar endpoints protegidos

¡Disfruta usando la API! 🚀

