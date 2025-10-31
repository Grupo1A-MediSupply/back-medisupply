#!/bin/bash

# ==============================================================================
# Script para probar todos los endpoints desplegados en Cloud Run
# ==============================================================================

set -e

cd "$(dirname "$0")"

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Obtener URLs
AUTH_URL=$(terraform output -raw auth_service_url 2>/dev/null)
PRODUCT_URL=$(terraform output -raw product_service_url 2>/dev/null)
ORDER_URL=$(terraform output -raw order_service_url 2>/dev/null)
LOGISTICS_URL=$(terraform output -raw logistics_service_url 2>/dev/null)
NOTIFICATIONS_URL=$(terraform output -raw notifications_service_url 2>/dev/null)

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}        🧪 PRUEBA COMPLETA DE ENDPOINTS EN CLOUD RUN${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Función para probar endpoint
test_endpoint() {
    local method=$1
    local url=$2
    local data=$3
    local description=$4
    
    echo -e "${BLUE}📝 $description${NC}"
    echo "   $method $url"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$url")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$url" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    http_code=$(echo "$response" | tail -1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "   ${GREEN}✅ HTTP $http_code${NC}"
        echo "$body" | python3 -m json.tool 2>/dev/null | head -5 || echo "$body" | head -3
    elif [ "$http_code" -ge 400 ] && [ "$http_code" -lt 500 ]; then
        echo -e "   ${YELLOW}⚠️  HTTP $http_code (Esperado para algunos casos)${NC}"
        echo "$body" | python3 -m json.tool 2>/dev/null | head -3 || echo "$body" | head -2
    else
        echo -e "   ${RED}❌ HTTP $http_code${NC}"
        echo "$body" | head -3
    fi
    echo ""
}

# ============================================================================
# AUTH SERVICE
# ============================================================================
echo -e "${BLUE}1️⃣  AUTH SERVICE${NC}"
echo "───────────────────────────────────────────────────────────"
echo ""

test_endpoint "POST" "$AUTH_URL/api/v1/auth/register" \
    '{"email":"test@example.com","username":"testuser","password":"Test123!","confirm_password":"Test123!","full_name":"Test User"}' \
    "POST /api/v1/auth/register - Registrar usuario"

test_endpoint "POST" "$AUTH_URL/api/v1/auth/login" \
    '{"username":"testuser","password":"Test123!"}' \
    "POST /api/v1/auth/login - Login"

test_endpoint "GET" "$AUTH_URL/api/v1/auth/verify" \
    "" \
    "GET /api/v1/auth/verify - Verificar token"

# ============================================================================
# PRODUCT SERVICE
# ============================================================================
echo -e "${BLUE}2️⃣  PRODUCT SERVICE${NC}"
echo "───────────────────────────────────────────────────────────"
echo ""

test_endpoint "GET" "$PRODUCT_URL/api/v1/products" \
    "" \
    "GET /api/v1/products - Listar productos"

test_endpoint "POST" "$PRODUCT_URL/api/v1/products" \
    '{"name":"Producto Test","description":"Descripción test","price":99.99,"stock":50}' \
    "POST /api/v1/products - Crear producto"

# ============================================================================
# ORDER SERVICE
# ============================================================================
echo -e "${BLUE}3️⃣  ORDER SERVICE${NC}"
echo "───────────────────────────────────────────────────────────"
echo ""

test_endpoint "GET" "$ORDER_URL/api/v1/orders" \
    "" \
    "GET /api/v1/orders - Listar órdenes"

test_endpoint "POST" "$ORDER_URL/api/v1/orders" \
    '{"items":[{"skuId":"SKU001","qty":2,"price":10.0}]}' \
    "POST /api/v1/orders - Crear orden"

# ============================================================================
# LOGISTICS SERVICE
# ============================================================================
echo -e "${BLUE}4️⃣  LOGISTICS SERVICE${NC}"
echo "───────────────────────────────────────────────────────────"
echo ""

test_endpoint "GET" "$LOGISTICS_URL/api/v1/routes" \
    "" \
    "GET /api/v1/routes - Listar rutas"

test_endpoint "POST" "$LOGISTICS_URL/api/v1/routes" \
    '{"stops":[{"orderId":"ORD001","priority":1}],"vehicleId":"VEH001"}' \
    "POST /api/v1/routes - Crear ruta"

# ============================================================================
# NOTIFICATIONS SERVICE
# ============================================================================
echo -e "${BLUE}5️⃣  NOTIFICATIONS SERVICE${NC}"
echo "───────────────────────────────────────────────────────────"
echo ""

test_endpoint "GET" "$NOTIFICATIONS_URL/api/v1/notifications" \
    "" \
    "GET /api/v1/notifications - Listar notificaciones"

test_endpoint "PUT" "$NOTIFICATIONS_URL/api/v1/notifications/notif_001/read" \
    "" \
    "PUT /api/v1/notifications/{id}/read - Marcar como leída"

# ============================================================================
# RESUMEN
# ============================================================================
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ Pruebas completadas${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""

