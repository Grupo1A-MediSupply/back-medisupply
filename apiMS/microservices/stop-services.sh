#!/bin/bash

echo "🛑 Deteniendo servicios MediSupply..."

# Cambiar al directorio correcto
cd "$(dirname "$0")"

# Detener contenedores
docker-compose down

echo "✅ Servicios detenidos"

