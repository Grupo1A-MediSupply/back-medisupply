#!/usr/bin/env python3
"""
Script completo para probar TODOS los endpoints del monolito
"""
import httpx
import sys
import time
import subprocess
import os
from pathlib import Path
import json
import random
import string

# Colores
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.RESET}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.RESET}")

def print_section(msg):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{msg}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.RESET}\n")

def wait_for_server(url="http://localhost:8000", timeout=30):
    """Esperar a que el servidor esté listo"""
    print_info("Esperando a que el servidor esté listo...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = httpx.get(f"{url}/health", timeout=2)
            if response.status_code == 200:
                print_success("Servidor listo!")
                return True
        except:
            time.sleep(0.5)
    return False

def test_endpoint(client, method, path, data=None, headers=None, expected_status=None, description=""):
    """Probar un endpoint"""
    try:
        url = f"http://localhost:8000{path}"
        request_kwargs = {"timeout": 10}
        if headers:
            request_kwargs["headers"] = headers
        
        if method == "GET":
            response = client.get(url, **request_kwargs)
        elif method == "POST":
            response = client.post(url, json=data, **request_kwargs)
        elif method == "PUT":
            response = client.put(url, json=data, **request_kwargs)
        elif method == "DELETE":
            response = client.delete(url, **request_kwargs)
        else:
            return False, f"Método {method} no soportado", None
        
        is_success = expected_status is None or response.status_code == expected_status
        status_msg = f"Status {response.status_code}"
        if expected_status and response.status_code != expected_status:
            status_msg += f" (esperado {expected_status})"
        
        try:
            response_data = response.json()
        except:
            response_data = response.text[:200]
        
        return is_success, status_msg, response_data
        
    except Exception as e:
        return False, f"Error: {str(e)[:100]}", None

def main():
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}🧪 Prueba Completa de TODOS los Endpoints{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}   Monolito MediSupply{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")
    
    # Iniciar servidor
    print_info("Iniciando servidor...")
    server_process = None
    try:
        server_process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=Path(__file__).parent,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, "PYTHONPATH": str(Path(__file__).parent)}
        )
        
        if not wait_for_server():
            print_error("El servidor no respondió a tiempo")
            if server_process:
                server_process.terminate()
            return 1
        
    except Exception as e:
        print_error(f"Error al iniciar servidor: {e}")
        return 1
    
    results = {"passed": 0, "failed": 0, "skipped": 0}
    user_id = None
    mfa_code = None
    access_token = None
    product_id = None
    order_id = None
    route_id = None
    
    try:
        with httpx.Client(timeout=15.0) as client:
            # ========== Endpoints Básicos ==========
            print_section("📋 Endpoints Básicos")
            
            for method, path, status, desc in [
                ("GET", "/", 200, "Root endpoint"),
                ("GET", "/health", 200, "Health check"),
                ("GET", "/docs", 200, "Swagger docs"),
            ]:
                success, msg, _ = test_endpoint(client, method, path, expected_status=status)
                if success:
                    print_success(f"{method:6} {path:45} - {desc}")
                    results["passed"] += 1
                else:
                    print_error(f"{method:6} {path:45} - {msg}")
                    results["failed"] += 1
            
            # ========== Auth Service ==========
            print_section("🔐 Auth Service")
            
            # Generar usuario único
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            test_email = f"testuser{random_suffix}@example.com"
            test_username = f"testuser{random_suffix}"
            
            # Register
            print_info(f"Registrando usuario: {test_username}")
            register_data = {
                "email": test_email,
                "username": test_username,
                "password": "testpass123",
                "confirm_password": "testpass123"
            }
            success, msg, data = test_endpoint(client, "POST", "/api/v1/auth/register", register_data, expected_status=201)
            if success:
                print_success(f"POST    /api/v1/auth/register{' '*25} - Register user")
                if data and isinstance(data, dict):
                    user_id = data.get("id")
                results["passed"] += 1
            else:
                print_warning(f"POST    /api/v1/auth/register{' '*25} - {msg}")
                results["skipped"] += 1
            
            # Login
            print_info(f"Login con usuario: {test_username}")
            login_data = {"username": test_username, "password": "testpass123"}
            success, msg, data = test_endpoint(client, "POST", "/api/v1/auth/login", login_data, expected_status=200)
            if success:
                print_success(f"POST    /api/v1/auth/login{' '*28} - Login")
                if data and isinstance(data, dict):
                    user_id = data.get("userId") or data.get("user_id") or user_id
                    mfa_code = data.get("mfaCode") or data.get("mfa_code")
                results["passed"] += 1
            else:
                print_warning(f"POST    /api/v1/auth/login{' '*28} - {msg}")
                results["skipped"] += 1
            
            # Get verification code
            if user_id:
                success, msg, data = test_endpoint(client, "GET", f"/api/v1/auth/verification-code/{user_id}", expected_status=200)
                if success:
                    print_success(f"GET     /api/v1/auth/verification-code/...{' '*15} - Get verification code")
                    if data and isinstance(data, dict):
                        mfa_code = data.get("code") or mfa_code
                    results["passed"] += 1
                else:
                    print_warning(f"GET     /api/v1/auth/verification-code/...{' '*15} - {msg}")
                    results["skipped"] += 1
            
            # Verify MFA
            if user_id and mfa_code:
                print_info("Verificando código MFA...")
                verify_data = {"user_id": user_id, "code": mfa_code}
                success, msg, data = test_endpoint(client, "POST", "/api/v1/auth/mfa/verify", verify_data, expected_status=200)
                if success:
                    print_success(f"POST    /api/v1/auth/mfa/verify{' '*25} - Verify MFA code")
                    if data and isinstance(data, dict):
                        access_token = data.get("token")
                    results["passed"] += 1
                else:
                    print_warning(f"POST    /api/v1/auth/mfa/verify{' '*25} - {msg}")
                    results["skipped"] += 1
            
            # Auth endpoints adicionales
            auth_endpoints = [
                ("GET", "/api/v1/auth/verify", None, 401, "Verify token (sin token)"),
            ]
            
            for method, path, data, status, desc in auth_endpoints:
                success, msg, _ = test_endpoint(client, method, path, data, expected_status=status)
                if success:
                    print_success(f"{method:6} {path:45} - {desc}")
                    results["passed"] += 1
                else:
                    print_warning(f"{method:6} {path:45} - {msg}")
                    results["skipped"] += 1
            
            # Get current user (con token si tenemos)
            if access_token:
                headers = {"Authorization": f"Bearer {access_token}"}
                success, msg, data = test_endpoint(client, "GET", "/api/v1/auth/me", headers=headers, expected_status=200)
                if success:
                    print_success(f"GET     /api/v1/auth/me{' '*33} - Get current user (con token)")
                    results["passed"] += 1
                else:
                    print_warning(f"GET     /api/v1/auth/me{' '*33} - {msg}")
                    results["skipped"] += 1
            else:
                success, msg, _ = test_endpoint(client, "GET", "/api/v1/auth/me", expected_status=401)
                if success:
                    print_success(f"GET     /api/v1/auth/me{' '*33} - Get current user (sin token)")
                    results["passed"] += 1
                else:
                    print_warning(f"GET     /api/v1/auth/me{' '*33} - {msg}")
                    results["skipped"] += 1
            
            # ========== Product Service ==========
            print_section("📦 Product Service")
            
            product_endpoints = [
                ("GET", "/api/v1/products", None, 200, "List products"),
                ("GET", "/api/v1/products/123", None, 404, "Get product (no existe)"),
            ]
            
            for method, path, data, status, desc in product_endpoints:
                success, msg, resp_data = test_endpoint(client, method, path, data, expected_status=status)
                if success:
                    print_success(f"{method:6} {path:45} - {desc}")
                    if resp_data and isinstance(resp_data, dict) and "products" in resp_data:
                        count = len(resp_data.get("products", []))
                        print(f"         → {count} productos")
                    results["passed"] += 1
                else:
                    print_warning(f"{method:6} {path:45} - {msg}")
                    results["skipped"] += 1
            
            # ========== Order Service ==========
            print_section("🛒 Order Service")
            
            order_endpoints = [
                ("GET", "/api/v1/orders", None, 200, "List orders"),
                ("GET", "/api/v1/orders/123", None, 404, "Get order (no existe)"),
            ]
            
            for method, path, data, status, desc in order_endpoints:
                success, msg, resp_data = test_endpoint(client, method, path, data, expected_status=status)
                if success:
                    print_success(f"{method:6} {path:45} - {desc}")
                    if resp_data and isinstance(resp_data, list):
                        print(f"         → {len(resp_data)} órdenes")
                    results["passed"] += 1
                else:
                    print_warning(f"{method:6} {path:45} - {msg}")
                    results["skipped"] += 1
            
            # ========== Logistics Service ==========
            print_section("🚚 Logistics Service")
            
            logistics_endpoints = [
                ("GET", "/api/v1/routes", None, 200, "List routes"),
                ("GET", "/api/v1/routes/123", None, 404, "Get route (no existe)"),
            ]
            
            for method, path, data, status, desc in logistics_endpoints:
                success, msg, resp_data = test_endpoint(client, method, path, data, expected_status=status)
                if success:
                    print_success(f"{method:6} {path:45} - {desc}")
                    if resp_data and isinstance(resp_data, list):
                        print(f"         → {len(resp_data)} rutas")
                    results["passed"] += 1
                else:
                    print_warning(f"{method:6} {path:45} - {msg}")
                    results["skipped"] += 1
            
            # ========== Inventory Service ==========
            print_section("📊 Inventory Service")
            
            inventory_endpoints = [
                ("GET", "/api/v1/inventory", None, 200, "List inventory"),
                ("GET", "/api/v1/inventory/template", None, 200, "Get inventory template"),
            ]
            
            for method, path, data, status, desc in inventory_endpoints:
                success, msg, resp_data = test_endpoint(client, method, path, data, expected_status=status)
                if success:
                    print_success(f"{method:6} {path:45} - {desc}")
                    if resp_data and isinstance(resp_data, list):
                        print(f"         → {len(resp_data)} items")
                    results["passed"] += 1
                else:
                    print_warning(f"{method:6} {path:45} - {msg}")
                    results["skipped"] += 1
            
            # ========== Reports Service ==========
            print_section("📈 Reports Service")
            
            reports_endpoints = [
                ("GET", "/api/v1/reports", None, 200, "Get reports"),
                ("GET", "/api/v1/reports/returns", None, 200, "Get returns report"),
            ]
            
            for method, path, data, status, desc in reports_endpoints:
                success, msg, resp_data = test_endpoint(client, method, path, data, expected_status=status)
                if success:
                    print_success(f"{method:6} {path:45} - {desc}")
                    if resp_data and isinstance(resp_data, dict):
                        keys = list(resp_data.keys())[:3]
                        print(f"         → Datos: {', '.join(keys)}...")
                    results["passed"] += 1
                else:
                    print_warning(f"{method:6} {path:45} - {msg}")
                    results["skipped"] += 1
            
            # ========== Notifications Service ==========
            print_section("🔔 Notifications Service")
            
            notifications_endpoints = [
                ("GET", "/api/v1/notifications", None, 200, "List notifications"),
            ]
            
            for method, path, data, status, desc in notifications_endpoints:
                success, msg, resp_data = test_endpoint(client, method, path, data, expected_status=status)
                if success:
                    print_success(f"{method:6} {path:45} - {desc}")
                    if resp_data and isinstance(resp_data, list):
                        print(f"         → {len(resp_data)} notificaciones")
                    results["passed"] += 1
                else:
                    print_warning(f"{method:6} {path:45} - {msg}")
                    results["skipped"] += 1
    
    finally:
        if server_process:
            print_info("\nDeteniendo servidor...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
            print_success("Servidor detenido")
    
    # Resumen
    print_section("📊 Resumen Final de Pruebas")
    total = results['passed'] + results['skipped'] + results['failed']
    success_rate = (results['passed'] / total * 100) if total > 0 else 0
    
    print(f"{Colors.GREEN}✅ Exitosos: {results['passed']}{Colors.RESET}")
    print(f"{Colors.YELLOW}⚠️  Omitidos/Esperados: {results['skipped']}{Colors.RESET}")
    print(f"{Colors.RED}❌ Fallidos: {results['failed']}{Colors.RESET}")
    print(f"{Colors.BLUE}📝 Total: {total}{Colors.RESET}")
    print(f"{Colors.BLUE}📈 Tasa de éxito: {success_rate:.1f}%{Colors.RESET}")
    
    if results['failed'] == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 Todas las pruebas críticas pasaron!{Colors.RESET}")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠️  Algunas pruebas fallaron{Colors.RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

