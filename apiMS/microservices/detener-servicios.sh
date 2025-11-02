#!/bin/bash

echo "🛑 Deteniendo todos los microservicios..."
echo ""

# Detener servicios por puerto
ports=(8001 8002 8003 8004 8005 8006 8007)
services=("Auth" "Product" "Order" "Logistics" "Inventory" "Reports" "Notifications")

for i in "${!ports[@]}"; do
    port="${ports[$i]}"
    service="${services[$i]}"
    
    pid=$(lsof -t -i:${port})
    
    if [ ! -z "$pid" ]; then
        kill -9 $pid 2>/dev/null
        echo "✅ ${service} Service (puerto ${port}) detenido"
    else
        echo "⚠️  ${service} Service (puerto ${port}) no estaba corriendo"
    fi
done

echo ""
echo "✅ Todos los servicios han sido detenidos"

