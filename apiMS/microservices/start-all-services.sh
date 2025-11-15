#!/bin/bash

# Script para iniciar todos los servicios manualmente en paralelo

echo "🚀 Iniciando servicios MediSupply (modo manual)..."

# Función para verificar si un puerto está en uso
check_port() {
    lsof -i :$1 > /dev/null 2>&1
    return $?
}

# Verificar puertos
echo "🔍 Verificando puertos..."
ports=(8001 8002 8003 8004)

for port in "${ports[@]}"; do
    if check_port $port; then
        echo "⚠️  Puerto $port ya está en uso"
    else
        echo "✅ Puerto $port disponible"
    fi
done

echo ""
echo "📝 Iniciando servicios en background..."
echo ""

# Iniciar Auth Service
cd auth-service && python -m uvicorn main:app --host 0.0.0.0 --port 8001 > ../logs/auth.log 2>&1 &
echo "✅ Auth Service iniciado en http://localhost:8001 (PID: $!)"

# Iniciar Product Service
cd ../product-service && python -m uvicorn main:app --host 0.0.0.0 --port 8002 > ../logs/product.log 2>&1 &
echo "✅ Product Service iniciado en http://localhost:8002 (PID: $!)"

# Iniciar Order Service
cd ../order-service && python -m uvicorn main:app --host 0.0.0.0 --port 8003 > ../logs/order.log 2>&1 &
echo "✅ Order Service iniciado en http://localhost:8003 (PID: $!)"

# Iniciar Logistics Service
cd ../logistics-service && python -m uvicorn main:app --host 0.0.0.0 --port 8004 > ../logs/logistics.log 2>&1 &
echo "✅ Logistics Service iniciado en http://localhost:8004 (PID: $!)"

echo ""
echo "⏳ Esperando a que los servicios inicien..."
sleep 10

echo ""
echo "🔍 Verificando salud de servicios..."
echo ""

check_service() {
    local service_name=$1
    local url=$2
    local port=$3
    
    response=$(curl -s -o /dev/null -w "%{http_code}" $url)
    
    if [ "$response" = "200" ]; then
        echo "✅ $service_name está funcionando (puerto $port)"
        return 0
    else
        echo "❌ $service_name NO responde (HTTP $response)"
        return 1
    fi
}

# Verificar servicios
check_service "Auth Service" "http://localhost:8001/health" 8001
check_service "Product Service" "http://localhost:8002/health" 8002
check_service "Order Service" "http://localhost:8003/health" 8003
check_service "Logistics Service" "http://localhost:8004/health" 8004

echo ""
echo "📋 URLs:"
echo "  - Auth: http://localhost:8001 (Docs: http://localhost:8001/docs)"
echo "  - Product: http://localhost:8002 (Docs: http://localhost:8002/docs)"
echo "  - Order: http://localhost:8003 (Docs: http://localhost:8003/docs)"
echo "  - Logistics: http://localhost:8004 (Docs: http://localhost:8004/docs)"
echo ""
echo "📝 Para ver logs: tail -f logs/*.log"
echo "🛑 Para detener: ./stop-all-services.sh"
echo ""

# Guardar PIDs en un archivo
echo $! > /tmp/auth.pid
echo $! > /tmp/product.pid
echo $! > /tmp/order.pid
echo $! > /tmp/logistics.pid

echo "🎉 ¡Servicios iniciados!"

