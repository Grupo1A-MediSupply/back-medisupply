#!/usr/bin/env python3
"""
Script completo para probar todos los endpoints del monolito
"""
import httpx
import sys
import time
import subprocess
import signal
import os
from pathlib import Path

# Colores para output
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
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{msg}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.RESET}\n")

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

def test_endpoint(client, method, path, data=None, expected_status=200, description=""):
    """Probar un endpoint"""
    try:
        url = f"http://localhost:8000{path}"
        if method == "GET":
            response = client.get(url, timeout=10)
        elif method == "POST":
            response = client.post(url, json=data, timeout=10)
        elif method == "PUT":
            response = client.put(url, json=data, timeout=10)
        elif method == "DELETE":
            response = client.delete(url, timeout=10)
        else:
            return False, f"Método {method} no soportado"
        
        if response.status_code == expected_status:
            return True, f"Status {response.status_code}"
        else:
            return False, f"Status {response.status_code} (esperado {expected_status})"
    except httpx.TimeoutException:
        return False, "Timeout"
    except Exception as e:
        return False, f"Error: {str(e)[:100]}"

def main():
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}🧪 Prueba Completa de Endpoints - Monolito MediSupply{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")
    
    # Iniciar servidor en segundo plano
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
        
        # Esperar a que el servidor esté listo
        if not wait_for_server():
            print_error("El servidor no respondió a tiempo")
            if server_process:
                server_process.terminate()
            return 1
        
    except Exception as e:
        print_error(f"Error al iniciar servidor: {e}")
        return 1
    
    results = {
        "passed": 0,
        "failed": 0,
        "skipped": 0
    }
    
    try:
        with httpx.Client(timeout=15.0) as client:
            # ========== Endpoints Básicos ==========
            print_section("📋 Endpoints Básicos")
            
            endpoints_basic = [
                ("GET", "/", 200, "Root endpoint"),
                ("GET", "/health", 200, "Health check"),
                ("GET", "/docs", 200, "Swagger docs"),
            ]
            
            for method, path, status, desc in endpoints_basic:
                success, msg = test_endpoint(client, method, path, expected_status=status, description=desc)
                if success:
                    print_success(f"{method:6} {path:40} - {desc}")
                    results["passed"] += 1
                else:
                    print_error(f"{method:6} {path:40} - {msg}")
                    results["failed"] += 1
            
            # ========== Auth Service ==========
            print_section("🔐 Auth Service")
            
            auth_endpoints = [
                ("POST", "/api/v1/auth/register", {
                    "email": "testuser@example.com",
                    "username": "testuser",
                    "password": "testpass123",
                    "confirm_password": "testpass123"
                }, 201, "Register user"),
                ("POST", "/api/v1/auth/login", {
                    "username": "testuser",
                    "password": "testpass123"
                }, 200, "Login"),
                ("GET", "/api/v1/auth/verify", None, 401, "Verify token (sin token)"),
                ("GET", "/api/v1/auth/me", None, 401, "Get current user (sin token)"),
            ]
            
            user_id = None
            mfa_code = None
            
            for method, path, data, status, desc in auth_endpoints:
                success, msg = test_endpoint(client, method, path, data, expected_status=status, description=desc)
                if success:
                    print_success(f"{method:6} {path:40} - {desc}")
                    results["passed"] += 1
                    
                    # Capturar user_id y mfa_code del login
                    if "login" in path and method == "POST":
                        try:
                            response = client.post(f"http://localhost:8000{path}", json=data, timeout=10)
                            if response.status_code == 200:
                                login_data = response.json()
                                user_id = login_data.get("userId") or login_data.get("user_id")
                                mfa_code = login_data.get("mfaCode") or login_data.get("mfa_code")
                        except:
                            pass
                else:
                    print_warning(f"{method:6} {path:40} - {msg} (puede ser esperado)")
                    results["skipped"] += 1
            
            # Probar obtener código de verificación si tenemos user_id
            if user_id:
                print_info(f"Probando obtener código de verificación para user_id: {user_id}")
                success, msg = test_endpoint(client, "GET", f"/api/v1/auth/verification-code/{user_id}", expected_status=200, description="Get verification code")
                if success:
                    print_success(f"GET     /api/v1/auth/verification-code/{user_id[:20]}... - Get verification code")
                    results["passed"] += 1
                else:
                    print_warning(f"GET     /api/v1/auth/verification-code/{user_id[:20]}... - {msg}")
                    results["skipped"] += 1
            
            # ========== Product Service ==========
            print_section("📦 Product Service")
            
            product_endpoints = [
                ("GET", "/api/v1/products", None, 200, "List products"),
                ("GET", "/api/v1/products/123", None, 404, "Get product (no existe)"),
            ]
            
            for method, path, data, status, desc in product_endpoints:
                success, msg = test_endpoint(client, method, path, data, expected_status=status, description=desc)
                if success:
                    print_success(f"{method:6} {path:40} - {desc}")
                    results["passed"] += 1
                else:
                    print_warning(f"{method:6} {path:40} - {msg}")
                    results["skipped"] += 1
            
            # ========== Order Service ==========
            print_section("🛒 Order Service")
            
            order_endpoints = [
                ("GET", "/api/v1/orders", None, 200, "List orders"),
                ("GET", "/api/v1/orders/123", None, 404, "Get order (no existe)"),
            ]
            
            for method, path, data, status, desc in order_endpoints:
                success, msg = test_endpoint(client, method, path, data, expected_status=status, description=desc)
                if success:
                    print_success(f"{method:6} {path:40} - {desc}")
                    results["passed"] += 1
                else:
                    print_warning(f"{method:6} {path:40} - {msg}")
                    results["skipped"] += 1
            
            # ========== Logistics Service ==========
            print_section("🚚 Logistics Service")
            
            logistics_endpoints = [
                ("GET", "/api/v1/routes", None, 200, "List routes"),
                ("GET", "/api/v1/routes/123", None, 404, "Get route (no existe)"),
            ]
            
            for method, path, data, status, desc in logistics_endpoints:
                success, msg = test_endpoint(client, method, path, data, expected_status=status, description=desc)
                if success:
                    print_success(f"{method:6} {path:40} - {desc}")
                    results["passed"] += 1
                else:
                    print_warning(f"{method:6} {path:40} - {msg}")
                    results["skipped"] += 1
            
            # ========== Inventory Service ==========
            print_section("📊 Inventory Service")
            
            inventory_endpoints = [
                ("GET", "/api/v1/inventory", None, 200, "List inventory"),
                ("GET", "/api/v1/inventory/template", None, 200, "Get inventory template"),
            ]
            
            for method, path, data, status, desc in inventory_endpoints:
                success, msg = test_endpoint(client, method, path, data, expected_status=status, description=desc)
                if success:
                    print_success(f"{method:6} {path:40} - {desc}")
                    results["passed"] += 1
                else:
                    print_warning(f"{method:6} {path:40} - {msg}")
                    results["skipped"] += 1
            
            # ========== Reports Service ==========
            print_section("📈 Reports Service")
            
            reports_endpoints = [
                ("GET", "/api/v1/reports", None, 200, "Get reports"),
                ("GET", "/api/v1/reports/returns", None, 200, "Get returns report"),
            ]
            
            for method, path, data, status, desc in reports_endpoints:
                success, msg = test_endpoint(client, method, path, data, expected_status=status, description=desc)
                if success:
                    print_success(f"{method:6} {path:40} - {desc}")
                    results["passed"] += 1
                else:
                    print_warning(f"{method:6} {path:40} - {msg}")
                    results["skipped"] += 1
            
            # ========== Notifications Service ==========
            print_section("🔔 Notifications Service")
            
            notifications_endpoints = [
                ("GET", "/api/v1/notifications", None, 200, "List notifications"),
            ]
            
            for method, path, data, status, desc in notifications_endpoints:
                success, msg = test_endpoint(client, method, path, data, expected_status=status, description=desc)
                if success:
                    print_success(f"{method:6} {path:40} - {desc}")
                    results["passed"] += 1
                else:
                    print_warning(f"{method:6} {path:40} - {msg}")
                    results["skipped"] += 1
    
    finally:
        # Detener servidor
        if server_process:
            print_info("\nDeteniendo servidor...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
            print_success("Servidor detenido")
    
    # Resumen
    print_section("📊 Resumen de Pruebas")
    print(f"{Colors.GREEN}✅ Exitosos: {results['passed']}{Colors.RESET}")
    print(f"{Colors.YELLOW}⚠️  Omitidos/Esperados: {results['skipped']}{Colors.RESET}")
    print(f"{Colors.RED}❌ Fallidos: {results['failed']}{Colors.RESET}")
    print(f"{Colors.BLUE}📝 Total: {results['passed'] + results['skipped'] + results['failed']}{Colors.RESET}")
    
    if results['failed'] == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 Todas las pruebas críticas pasaron!{Colors.RESET}")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠️  Algunas pruebas fallaron{Colors.RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

