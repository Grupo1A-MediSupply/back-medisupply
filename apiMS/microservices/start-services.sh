#!/bin/bash

echo "🚀 Iniciando servicios MediSupply..."

# Cambiar al directorio correcto
cd "$(dirname "$0")"

# Iniciar con Docker Compose
echo "📦 Iniciando contenedores..."
docker-compose up -d

# Esperar a que los servicios inicien
echo "⏳ Esperando a que los servicios inicien..."
sleep 15

# Verificar salud de cada servicio
echo ""
echo "🔍 Verificando salud de servicios..."
echo ""

check_service() {
    local service_name=$1
    local url=$2
    
    response=$(curl -s -o /dev/null -w "%{http_code}" $url)
    
    if [ "$response" = "200" ]; then
        echo "✅ $service_name está funcionando"
        return 0
    else
        echo "❌ $service_name NO responde (HTTP $response)"
        return 1
    fi
}

# Verificar servicios
check_service "Auth Service" "http://localhost:8001/health"
check_service "Product Service" "http://localhost:8002/health"
check_service "Order Service" "http://localhost:8003/health"
check_service "Logistics Service" "http://localhost:8004/health"

echo ""
echo "📋 URLs de servicios:"
echo "  - Auth Service: http://localhost:8001"
echo "  - Product Service: http://localhost:8002"
echo "  - Order Service: http://localhost:8003"
echo "  - Logistics Service: http://localhost:8004"
echo ""
echo "📖 Documentación:"
echo "  - Auth Docs: http://localhost:8001/docs"
echo "  - Product Docs: http://localhost:8002/docs"
echo "  - Order Docs: http://localhost:8003/docs"
echo "  - Logistics Docs: http://localhost:8004/docs"
echo ""

# Ver logs
echo "📝 Para ver los logs, ejecuta:"
echo "  docker-compose logs -f"
echo ""

echo "🎉 ¡Servicios iniciados!"

