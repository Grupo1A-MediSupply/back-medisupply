#!/bin/bash
# ==============================================================================
# Script para validar que el backend está guardando correctamente en Cloud SQL
# ==============================================================================

set -e

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ID="project-65436llm"
INSTANCE_NAME="project-65436llm-postgres-instance"
REGION="us-central1"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Validación de Conexión a Cloud SQL${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Función para verificar comandos
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}❌ $1 no está instalado${NC}"
        return 1
    fi
    return 0
}

# Verificar dependencias
echo -e "${YELLOW}Verificando dependencias...${NC}"
check_command gcloud || exit 1
check_command psql || echo -e "${YELLOW}⚠️  psql no está instalado. Instálalo con: brew install postgresql${NC}"
echo ""

# 1. Verificar que la instancia existe y está activa
echo -e "${BLUE}[1/6] Verificando instancia de Cloud SQL...${NC}"
INSTANCE_STATUS=$(gcloud sql instances describe $INSTANCE_NAME --format='get(state)' 2>/dev/null || echo "NOT_FOUND")

if [ "$INSTANCE_STATUS" = "NOT_FOUND" ]; then
    echo -e "${RED}❌ La instancia no existe o no tienes permisos${NC}"
    exit 1
elif [ "$INSTANCE_STATUS" != "RUNNABLE" ]; then
    echo -e "${YELLOW}⚠️  Instancia en estado: $INSTANCE_STATUS${NC}"
else
    echo -e "${GREEN}✅ Instancia activa (RUNNABLE)${NC}"
fi
echo ""

# 2. Verificar bases de datos
echo -e "${BLUE}[2/6] Verificando bases de datos...${NC}"
DATABASES=("auth_service" "product_service" "order_service" "logistics_service" "notifications_service")

for db in "${DATABASES[@]}"; do
    # Intentar listar la base de datos usando gcloud
    if gcloud sql databases describe $db --instance=$INSTANCE_NAME &>/dev/null; then
        echo -e "${GREEN}✅ Base de datos '$db' existe${NC}"
    else
        echo -e "${RED}❌ Base de datos '$db' NO existe${NC}"
    fi
done
echo ""

# 3. Verificar usuarios
echo -e "${BLUE}[3/6] Verificando usuarios...${NC}"
USERS=("auth_service_user" "product_service_user" "order_service_user" "logistics_service_user" "notifications_service_user" "postgres")

for user in "${USERS[@]}"; do
    if gcloud sql users describe $user --instance=$INSTANCE_NAME &>/dev/null; then
        echo -e "${GREEN}✅ Usuario '$user' existe${NC}"
    else
        echo -e "${YELLOW}⚠️  Usuario '$user' NO existe${NC}"
    fi
done
echo ""

# 4. Verificar configuración de Cloud Run
echo -e "${BLUE}[4/6] Verificando configuración de Cloud Run...${NC}"
SERVICES=("auth-service" "product-service" "order-service" "logistics-service" "notifications-service")

for service in "${SERVICES[@]}"; do
    echo -n "  Verificando $service... "
    
    # Verificar si el servicio existe
    if gcloud run services describe $service --region=$REGION &>/dev/null; then
        # Obtener la URL de la base de datos configurada
        DB_URL_ENV=$(gcloud run services describe $service --region=$REGION --format='get(spec.template.spec.containers[0].env)' 2>/dev/null | grep -i "DATABASE_URL" || echo "")
        
        if echo "$DB_URL_ENV" | grep -q "cloudsql"; then
            echo -e "${GREEN}✅ Configurado con Cloud SQL${NC}"
        elif echo "$DB_URL_ENV" | grep -q "sqlite"; then
            echo -e "${YELLOW}⚠️  Usando SQLite (no Cloud SQL)${NC}"
        else
            echo -e "${YELLOW}⚠️  No se encontró DATABASE_URL${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Servicio no encontrado${NC}"
    fi
done
echo ""

# 5. Verificar logs recientes de Cloud Run para errores de conexión
echo -e "${BLUE}[5/6] Verificando logs recientes de Cloud Run...${NC}"
for service in "${SERVICES[@]}"; do
    echo "  Revisando logs de $service..."
    
    # Buscar errores de conexión en los últimos 100 logs
    ERRORS=$(gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$service AND (textPayload=~'database' OR textPayload=~'connection' OR textPayload=~'SQL')" --limit=10 --format='get(textPayload)' 2>/dev/null | grep -i -E "(error|fail|exception|timeout)" || echo "")
    
    if [ -z "$ERRORS" ]; then
        echo -e "    ${GREEN}✅ No se encontraron errores recientes de base de datos${NC}"
    else
        echo -e "    ${RED}❌ Se encontraron posibles errores:${NC}"
        echo "$ERRORS" | head -3 | sed 's/^/      /'
    fi
done
echo ""

# 6. Prueba de conexión directa (si psql está disponible)
if command -v psql &> /dev/null; then
    echo -e "${BLUE}[6/6] Prueba de conexión directa...${NC}"
    echo -e "${YELLOW}  (Requiere Cloud SQL Proxy o IP autorizada)${NC}"
    
    # Intentar obtener contraseña
    PASSWORD=$(gcloud secrets versions access latest --secret="auth-service-db-password" 2>/dev/null || echo "")
    
    if [ -z "$PASSWORD" ]; then
        echo -e "${YELLOW}  ⚠️  No se pudo obtener la contraseña automáticamente${NC}"
        echo -e "${YELLOW}  Para probar la conexión manualmente:${NC}"
        echo -e "${YELLOW}    1. Inicia Cloud SQL Proxy${NC}"
        echo -e "${YELLOW}    2. psql -h 127.0.0.1 -p 5432 -U auth_service_user -d auth_service${NC}"
    else
        echo -e "${GREEN}  ✅ Contraseña obtenida de Secret Manager${NC}"
        echo -e "${YELLOW}  Para probar la conexión:${NC}"
        echo -e "${YELLOW}    1. Inicia Cloud SQL Proxy en otra terminal${NC}"
        echo -e "${YELLOW}    2. PGPASSWORD='$PASSWORD' psql -h 127.0.0.1 -p 5432 -U auth_service_user -d auth_service${NC}"
    fi
else
    echo -e "${YELLOW}[6/6] Saltando prueba de conexión (psql no disponible)${NC}"
fi
echo ""

# Resumen
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Resumen${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Para verificar que los datos se están guardando:"
echo ""
echo "1. Revisa los logs de Cloud Run:"
echo -e "   ${YELLOW}gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=auth-service\" --limit=50${NC}"
echo ""
echo "2. Conéctate a la base de datos y verifica datos:"
echo -e "   ${YELLOW}./connect-to-cloud-sql.sh auto auth_service auth_service_user${NC}"
echo ""
echo "3. Prueba crear un registro desde la API:"
echo -e "   ${YELLOW}# Obtén la URL del servicio${NC}"
echo -e "   ${YELLOW}gcloud run services describe auth-service --region=$REGION --format='get(status.url)'${NC}"
echo ""
echo "4. Verifica en la base de datos que el registro se guardó:"
echo -e "   ${YELLOW}# Después de conectarte con psql${NC}"
echo -e "   ${YELLOW}SELECT * FROM users LIMIT 5;${NC}"
echo ""

