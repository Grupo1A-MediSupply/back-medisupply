#!/bin/bash

echo "🚀 Iniciando todos los microservicios de MediSupply..."
echo ""

# Directorio base
BASE_DIR="/Users/lucasblandon/PROYECTOFINAL/codigoV5/apiMS/microservices"

# Función para iniciar servicio
start_service() {
    local service_name=$1
    local port=$2
    local service_dir="${BASE_DIR}/${service_name}"
    
    echo "📦 Iniciando ${service_name} en puerto ${port}..."
    
    cd "$BASE_DIR"
    python -m uvicorn ${service_name}.main:app --host 0.0.0.0 --port ${port} --reload > "/tmp/${service_name}.log" 2>&1 &
    
    local pid=$!
    echo "   ✅ ${service_name} iniciado (PID: ${pid})"
    echo ""
}

# Iniciar servicios
start_service "auth-service" 8001
sleep 2
start_service "product-service" 8002
sleep 2
start_service "order-service" 8003
sleep 2
start_service "logistics-service" 8004
sleep 2
start_service "inventory-service" 8005
sleep 2
start_service "reports-service" 8006
sleep 2
start_service "notifications-service" 8007

echo "⏳ Esperando 10 segundos para que los servicios inicien..."
sleep 10

echo ""
echo "🔍 Verificando servicios..."
echo ""

# Verificar servicios
check_service() {
    local name=$1
    local port=$2
    
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:${port}/health)
    
    if [ "$response" = "200" ]; then
        echo "✅ ${name} (puerto ${port}) - OK"
    else
        echo "❌ ${name} (puerto ${port}) - NO responde (HTTP ${response})"
    fi
}

check_service "Auth Service" 8001
check_service "Product Service" 8002
check_service "Order Service" 8003
check_service "Logistics Service" 8004
check_service "Inventory Service" 8005
check_service "Reports Service" 8006
check_service "Notifications Service" 8007

echo ""
echo "📋 URLs de servicios:"
echo "  - Auth: http://localhost:8001 (Docs: http://localhost:8001/docs)"
echo "  - Product: http://localhost:8002 (Docs: http://localhost:8002/docs)"
echo "  - Order: http://localhost:8003 (Docs: http://localhost:8003/docs)"
echo "  - Logistics: http://localhost:8004 (Docs: http://localhost:8004/docs)"
echo "  - Inventory: http://localhost:8005 (Docs: http://localhost:8005/docs)"
echo "  - Reports: http://localhost:8006 (Docs: http://localhost:8006/docs)"
echo "  - Notifications: http://localhost:8007 (Docs: http://localhost:8007/docs)"
echo ""

echo "📝 Para ver logs:"
echo "  tail -f /tmp/auth-service.log"
echo "  tail -f /tmp/product-service.log"
echo "  tail -f /tmp/order-service.log"
echo "  tail -f /tmp/logistics-service.log"
echo "  tail -f /tmp/inventory-service.log"
echo "  tail -f /tmp/reports-service.log"
echo "  tail -f /tmp/notifications-service.log"
echo ""

echo "🛑 Para detener servicios:"
echo "  ./detener-servicios.sh"
echo ""

echo "🎉 ¡Servicios iniciados!"

