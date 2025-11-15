#!/bin/bash

echo "🛑 Deteniendo servicios MediSupply..."

# Matar procesos en los puertos
kill -9 $(lsof -t -i :8001) 2>/dev/null && echo "✅ Auth Service detenido" || echo "⚠️  Auth Service no estaba corriendo"
kill -9 $(lsof -t -i :8002) 2>/dev/null && echo "✅ Product Service detenido" || echo "⚠️  Product Service no estaba corriendo"
kill -9 $(lsof -t -i :8003) 2>/dev/null && echo "✅ Order Service detenido" || echo "⚠️  Order Service no estaba corriendo"
kill -9 $(lsof -t -i :8004) 2>/dev/null && echo "✅ Logistics Service detenido" || echo "⚠️  Logistics Service no estaba corriendo"

echo ""
echo "✅ Servicios detenidos"

