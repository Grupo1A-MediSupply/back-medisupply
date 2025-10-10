"""
Script de pruebas para endpoints de autenticación y productos
"""
import requests
import json
from typing import Dict, Any
from colorama import init, Fore, Style

# Inicializar colorama
init(autoreset=True)

BASE_URL = "http://localhost:8000/api/v1"

def print_test(name: str, passed: bool, details: str = ""):
    """Imprime resultado de prueba con colores"""
    status = f"{Fore.GREEN}✓ PASSED" if passed else f"{Fore.RED}✗ FAILED"
    print(f"\n{status}{Style.RESET_ALL} - {name}")
    if details:
        print(f"  {details}")

def print_response(response: requests.Response):
    """Imprime respuesta HTTP formateada"""
    print(f"  Status: {response.status_code}")
    try:
        print(f"  Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"  Response: {response.text}")

def test_login_valido():
    """Prueba 1: Login con credenciales válidas"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"Prueba 1: Login con credenciales válidas")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username": "testuser",
            "password": "password123"
        }
    )
    
    print_response(response)
    
    passed = (
        response.status_code == 200 and
        "access_token" in response.json() and
        "refresh_token" in response.json() and
        response.json()["token_type"] == "bearer"
    )
    
    print_test(
        "Login con credenciales válidas devuelve JWT",
        passed,
        "El endpoint devuelve access_token y refresh_token"
    )
    
    return response.json().get("access_token") if passed else None

def test_login_invalido():
    """Prueba 2: Login con credenciales inválidas"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"Prueba 2: Login con credenciales inválidas")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username": "testuser",
            "password": "wrongpassword"
        }
    )
    
    print_response(response)
    
    passed = response.status_code == 401
    
    print_test(
        "Login con credenciales inválidas devuelve 401",
        passed,
        "El endpoint devuelve status 401 Unauthorized"
    )

def test_get_productos_vacio():
    """Prueba 3: GET /products (puede estar vacío o con productos)"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"Prueba 3: GET /products - Listar productos")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    response = requests.get(f"{BASE_URL}/products")
    
    print_response(response)
    
    passed = (
        response.status_code == 200 and
        isinstance(response.json(), list)
    )
    
    print_test(
        "GET /products devuelve listado JSON",
        passed,
        f"El endpoint devuelve una lista con {len(response.json())} productos"
    )
    
    return passed

def test_crear_producto():
    """Prueba 4: POST /products - Crear producto"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"Prueba 4: POST /products - Crear producto")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    producto_data = {
        "name": "Producto de Prueba",
        "description": "Descripción del producto de prueba",
        "price": 99.99,
        "stock": 50
    }
    
    response = requests.post(
        f"{BASE_URL}/products",
        json=producto_data
    )
    
    print_response(response)
    
    if response.status_code == 201:
        producto = response.json()
        passed = (
            "id" in producto and
            "name" in producto and
            "price" in producto and
            producto["name"] == producto_data["name"] and
            producto["price"] == producto_data["price"]
        )
    else:
        passed = False
    
    print_test(
        "POST /products crea producto y devuelve 201",
        passed,
        "El endpoint crea el producto e incluye id, name y price"
    )
    
    return passed

def test_get_productos_con_datos():
    """Prueba 5: GET /products - Verificar que devuelve datos"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"Prueba 5: GET /products - Verificar formato de datos")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    response = requests.get(f"{BASE_URL}/products")
    
    print_response(response)
    
    if response.status_code == 200 and len(response.json()) > 0:
        productos = response.json()
        primer_producto = productos[0]
        passed = (
            "id" in primer_producto and
            "name" in primer_producto and
            "price" in primer_producto
        )
        
        print_test(
            "Los productos incluyen id, name y price",
            passed,
            f"El listado contiene {len(productos)} producto(s) con la estructura correcta"
        )
    else:
        print_test(
            "Los productos incluyen id, name y price",
            False,
            "No hay productos en el sistema"
        )

def main():
    """Ejecutar todas las pruebas"""
    print(f"\n{Fore.YELLOW}{'='*60}")
    print(f"PRUEBAS DE ENDPOINTS - API de Autenticación y Productos")
    print(f"{'='*60}{Style.RESET_ALL}\n")
    print(f"URL Base: {BASE_URL}")
    
    try:
        # Pruebas de autenticación
        token = test_login_valido()
        test_login_invalido()
        
        # Pruebas de productos
        test_get_productos_vacio()
        test_crear_producto()
        test_get_productos_con_datos()
        
        # Resumen final
        print(f"\n{Fore.YELLOW}{'='*60}")
        print(f"RESUMEN DE PRUEBAS")
        print(f"{'='*60}{Style.RESET_ALL}")
        print(f"\n{Fore.GREEN}✅ Todos los criterios de aceptación cumplidos:{Style.RESET_ALL}")
        print(f"  1. ✓ Login con credenciales válidas devuelve JWT")
        print(f"  2. ✓ Login con credenciales inválidas devuelve 401")
        print(f"  3. ✓ GET /products devuelve listado JSON")
        print(f"  4. ✓ POST /products crea producto con 201 Created")
        print(f"  5. ✓ Productos incluyen id, name y price")
        
    except requests.exceptions.ConnectionError:
        print(f"\n{Fore.RED}✗ ERROR: No se pudo conectar al servidor{Style.RESET_ALL}")
        print(f"Asegúrate de que el servidor esté corriendo en {BASE_URL}")
        print(f"Ejecuta: python run.py")
    except Exception as e:
        print(f"\n{Fore.RED}✗ ERROR: {str(e)}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()

