"""
API Gateway - Punto de entrada unificado para todos los microservicios
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from contextlib import asynccontextmanager
import httpx
import os
from typing import Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URLs de los microservicios (desde variables de entorno o valores por defecto)
SERVICES = {
    "auth": os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001"),
    "products": os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8002"),
    "orders": os.getenv("ORDER_SERVICE_URL", "http://order-service:8003"),
    "logistics": os.getenv("LOGISTICS_SERVICE_URL", "http://logistics-service:8004"),
    "inventory": os.getenv("INVENTORY_SERVICE_URL", "http://inventory-service:8005"),
    "reports": os.getenv("REPORTS_SERVICE_URL", "http://reports-service:8006"),
    "notifications": os.getenv("NOTIFICATIONS_SERVICE_URL", "http://notifications-service:8007"),
}

# Mapeo de rutas a servicios
ROUTE_MAPPING = {
    "/api/v1/auth": "auth",
    "/api/v1/products": "products",
    "/api/v1/orders": "orders",
    "/api/v1/routes": "logistics",
    "/api/v1/inventory": "inventory",
    "/api/v1/reports": "reports",
    "/api/v1/notifications": "notifications",
}

# Cliente HTTP asíncrono
http_client = httpx.AsyncClient(timeout=30.0)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    logger.info("🚀 Iniciando API Gateway")
    logger.info(f"Servicios configurados: {SERVICES}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Cerrando API Gateway")
    await http_client.aclose()


def create_app() -> FastAPI:
    """Factory para crear la aplicación FastAPI del Gateway"""
    
    app = FastAPI(
        title="MediSupply API Gateway",
        description="Gateway unificado para todos los microservicios",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # En producción, especificar orígenes permitidos
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    def get_service_from_path(path: str) -> Optional[tuple]:
        """Determina qué servicio maneja una ruta"""
        # Buscar la ruta más larga que coincida
        for route_prefix, service_name in sorted(ROUTE_MAPPING.items(), key=lambda x: len(x[0]), reverse=True):
            if path.startswith(route_prefix):
                service_url = SERVICES[service_name]
                # Retornar la ruta completa (el servicio espera /api/v1/...)
                # No remover el prefijo, pasar la ruta completa
                return service_name, service_url, path
        return None
    
    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
    async def proxy_request(path: str, request: Request):
        """Proxy todas las peticiones a los microservicios correspondientes"""
        try:
            # Construir la ruta completa (sin query string para el mapeo)
            full_path = f"/{path}" if not path.startswith("/") else path
            query_string = str(request.url.query)
            
            # Determinar el servicio destino (sin query string)
            service_info = get_service_from_path(full_path)
            
            if not service_info:
                # Si no hay mapeo, intentar rutas de health y root
                if full_path in ["/", "/health", "/docs", "/redoc", "/openapi.json"]:
                    # Estas rutas se manejan localmente
                    if full_path == "/":
                        return {
                            "service": "API Gateway",
                            "version": "1.0.0",
                            "description": "Gateway unificado para microservicios MediSupply",
                            "services": list(SERVICES.keys()),
                            "docs": "/docs"
                        }
                elif full_path == "/health":
                    # Health check del gateway
                    return {"status": "healthy", "service": "api-gateway"}
                else:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Ruta no encontrada: {full_path}"
                    )
            
            service_name, service_url, full_service_path = service_info
            
            # Construir URL completa del servicio destino
            # full_service_path ya contiene la ruta completa (ej: /api/v1/auth/verify)
            # Solo necesitamos agregar el query string si existe
            
            # Construir URL con query string si existe
            if query_string:
                separator = "&" if "?" in full_service_path else "?"
                target_url = f"{service_url}{full_service_path}{separator}{query_string}"
            else:
                target_url = f"{service_url}{full_service_path}"
            
            logger.info(f"Proxying {request.method} {full_path} -> {target_url}")
            
            # Obtener el cuerpo de la petición si existe
            body = None
            if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
                try:
                    body = await request.body()
                except Exception:
                    body = None
            
            # Obtener headers (excluyendo algunos que no deben propagarse)
            headers = dict(request.headers)
            headers_to_remove = ["host", "content-length", "connection"]
            for header in headers_to_remove:
                headers.pop(header, None)
            
            # Realizar la petición al servicio destino
            try:
                response = await http_client.request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    content=body,
                    follow_redirects=True
                )
                
                # Si es un streaming response (como archivos CSV), manejarlo de forma especial
                content_type = response.headers.get("content-type", "")
                if "text/csv" in content_type or "application/octet-stream" in content_type:
                    return StreamingResponse(
                        iter([response.content]),
                        media_type=content_type,
                        headers=dict(response.headers)
                    )
                
                # Retornar respuesta JSON
                return JSONResponse(
                    content=response.json() if response.content else {},
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
                
            except httpx.TimeoutException:
                logger.error(f"Timeout al conectar con {service_name} en {target_url}")
                raise HTTPException(
                    status_code=504,
                    detail=f"Timeout al conectar con el servicio {service_name}"
                )
            except httpx.ConnectError:
                logger.error(f"Error de conexión con {service_name} en {target_url}")
                raise HTTPException(
                    status_code=503,
                    detail=f"Servicio {service_name} no disponible"
                )
            except Exception as e:
                logger.error(f"Error al hacer proxy a {service_name}: {str(e)}")
                raise HTTPException(
                    status_code=502,
                    detail=f"Error al comunicarse con el servicio {service_name}: {str(e)}"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error inesperado en el gateway: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error interno del gateway: {str(e)}"
            )
    
    @app.get("/")
    async def root():
        """Endpoint raíz del gateway"""
        return {
            "service": "API Gateway",
            "version": "1.0.0",
            "description": "Gateway unificado para microservicios MediSupply",
            "base_url": "/api/v1",
            "services": {
                name: url for name, url in SERVICES.items()
            },
            "docs": "/docs"
        }
    
    @app.get("/health")
    async def health_check():
        """Health check del gateway y servicios"""
        health_status = {
            "gateway": "healthy",
            "services": {}
        }
        
        # Verificar salud de cada servicio
        for service_name, service_url in SERVICES.items():
            try:
                response = await http_client.get(f"{service_url}/health", timeout=5.0)
                health_status["services"][service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "url": service_url
                }
            except Exception as e:
                health_status["services"][service_name] = {
                    "status": "unhealthy",
                    "url": service_url,
                    "error": str(e)
                }
        
        return health_status
    
    return app


# Crear instancia de la aplicación
app = create_app()


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("GATEWAY_PORT", "8000"))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port
    )

