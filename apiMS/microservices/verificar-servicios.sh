#!/bin/bash

echo "🔍 Verificando estado de los microservicios..."
echo ""

check_service() {
    local name=$1
    local port=$2
    
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:${port}/health 2>/dev/null)
    
    if [ "$response" = "200" ]; then
        echo "✅ ${name} (puerto ${port}) - Funcionando"
        return 0
    else
        echo "❌ ${name} (puerto ${port}) - No responde"
        return 1
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
echo "📋 URLs de documentación:"
echo "  http://localhost:8001/docs - Auth Service"
echo "  http://localhost:8002/docs - Product Service"
echo "  http://localhost:8003/docs - Order Service"
echo "  http://localhost:8004/docs - Logistics Service"
echo "  http://localhost:8005/docs - Inventory Service"
echo "  http://localhost:8006/docs - Reports Service"
echo "  http://localhost:8007/docs - Notifications Service"

