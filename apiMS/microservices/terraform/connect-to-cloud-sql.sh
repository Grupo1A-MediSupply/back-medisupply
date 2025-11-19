#!/bin/bash
# ==============================================================================
# Script para conectarse a Cloud SQL PostgreSQL
# ==============================================================================
# Uso: ./connect-to-cloud-sql.sh [método] [database] [usuario]
# Métodos disponibles: proxy, cloud-shell, gcloud
# ==============================================================================

set -e

# Configuración
PROJECT_ID="project-65436llm"
INSTANCE_NAME="project-65436llm-postgres-instance"
REGION="us-central1"  # Ajusta según tu región

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Conectar a Cloud SQL PostgreSQL${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Función para obtener el connection name
get_connection_name() {
    echo "${PROJECT_ID}:${REGION}:${INSTANCE_NAME}"
}

# Método 1: Cloud SQL Proxy (Recomendado para desarrollo local)
method_proxy() {
    echo -e "${GREEN}Método 1: Cloud SQL Proxy${NC}"
    echo ""
    echo "1. Instala Cloud SQL Proxy si no lo tienes:"
    echo "   curl -o cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.8.0/cloud-sql-proxy.darwin.amd64"
    echo "   chmod +x cloud-sql-proxy"
    echo ""
    echo "2. Inicia el proxy en una terminal:"
    CONNECTION_NAME=$(get_connection_name)
    echo -e "${YELLOW}   ./cloud-sql-proxy ${CONNECTION_NAME}${NC}"
    echo ""
    echo "3. En otra terminal, conéctate con psql:"
    echo -e "${YELLOW}   psql -h 127.0.0.1 -p 5432 -U [usuario] -d [database]${NC}"
    echo ""
    echo "Bases de datos disponibles:"
    echo "  - auth_service"
    echo "  - product_service"
    echo "  - order_service"
    echo "  - logistics_service"
    echo "  - notifications_service"
    echo ""
    echo "Usuarios disponibles (obtén las contraseñas de Secret Manager):"
    echo "  - auth_service_user"
    echo "  - product_service_user"
    echo "  - order_service_user"
    echo "  - logistics_service_user"
    echo "  - notifications_service_user"
    echo "  - postgres (si configuraste db_root_password)"
}

# Método 2: Cloud Shell (Más fácil, sin instalación)
method_cloud_shell() {
    echo -e "${GREEN}Método 2: Desde Cloud Shell${NC}"
    echo ""
    echo "1. Abre Cloud Shell en: https://console.cloud.google.com"
    echo ""
    echo "2. Ejecuta este comando para conectarte:"
    CONNECTION_NAME=$(get_connection_name)
    echo -e "${YELLOW}   gcloud sql connect ${INSTANCE_NAME} --user=[usuario] --database=[database]${NC}"
    echo ""
    echo "Ejemplo:"
    echo -e "${YELLOW}   gcloud sql connect ${INSTANCE_NAME} --user=auth_service_user --database=auth_service${NC}"
}

# Método 3: gcloud directamente (requiere autorización de IP)
method_gcloud() {
    echo -e "${GREEN}Método 3: gcloud CLI directo${NC}"
    echo ""
    echo "1. Obtén tu IP pública:"
    echo "   curl ifconfig.me"
    echo ""
    echo "2. Agrega tu IP a authorized networks (temporalmente):"
    MY_IP=$(curl -s ifconfig.me)
    echo -e "${YELLOW}   gcloud sql instances patch ${INSTANCE_NAME} --authorized-networks=${MY_IP}/32${NC}"
    echo ""
    echo "3. Obtén la IP pública de la instancia:"
    echo -e "${YELLOW}   gcloud sql instances describe ${INSTANCE_NAME} --format='get(ipAddresses[0].ipAddress)'${NC}"
    echo ""
    echo "4. Conéctate con psql:"
    echo -e "${YELLOW}   psql -h [IP_PUBLICA] -U [usuario] -d [database]${NC}"
    echo ""
    echo "⚠️  Recuerda remover tu IP después:"
    echo -e "${YELLOW}   gcloud sql instances patch ${INSTANCE_NAME} --clear-authorized-networks${NC}"
}

# Método 4: Obtener contraseñas de Secret Manager
method_get_passwords() {
    echo -e "${GREEN}Obtener contraseñas de Secret Manager${NC}"
    echo ""
    echo "Las contraseñas están almacenadas en Secret Manager:"
    echo ""
    echo "1. Lista los secretos:"
    echo -e "${YELLOW}   gcloud secrets list${NC}"
    echo ""
    echo "2. Obtén una contraseña específica:"
    echo -e "${YELLOW}   gcloud secrets versions access latest --secret=\"auth-service-db-password\"${NC}"
    echo -e "${YELLOW}   gcloud secrets versions access latest --secret=\"product-service-db-password\"${NC}"
    echo -e "${YELLOW}   gcloud secrets versions access latest --secret=\"order-service-db-password\"${NC}"
    echo -e "${YELLOW}   gcloud secrets versions access latest --secret=\"logistics-service-db-password\"${NC}"
    echo -e "${YELLOW}   gcloud secrets versions access latest --secret=\"notifications-service-db-password\"${NC}"
}

# Método 5: Conectar con Cloud SQL Proxy automáticamente
method_proxy_auto() {
    DATABASE=${1:-"auth_service"}
    USER=${2:-"auth_service_user"}
    
    echo -e "${GREEN}Conectando automáticamente con Cloud SQL Proxy...${NC}"
    echo ""
    
    # Verificar si cloud-sql-proxy está instalado y obtener su ruta
    PROXY_CMD=""
    if command -v cloud-sql-proxy &> /dev/null; then
        PROXY_CMD="cloud-sql-proxy"
    elif [ -f "/usr/local/bin/cloud-sql-proxy" ]; then
        PROXY_CMD="/usr/local/bin/cloud-sql-proxy"
    elif [ -f "$HOME/cloud-sql-proxy" ]; then
        PROXY_CMD="$HOME/cloud-sql-proxy"
    elif [ -f "./cloud-sql-proxy" ]; then
        PROXY_CMD="./cloud-sql-proxy"
    else
        echo "❌ Cloud SQL Proxy no está instalado."
        echo "Instalando..."
        
        OS=$(uname -s | tr '[:upper:]' '[:lower:]')
        ARCH=$(uname -m)
        
        if [ "$ARCH" = "x86_64" ]; then
            ARCH="amd64"
        elif [ "$ARCH" = "arm64" ] || [ "$ARCH" = "aarch64" ]; then
            ARCH="arm64"
        fi
        
        PROXY_URL="https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.8.0/cloud-sql-proxy.${OS}.${ARCH}"
        
        # Descargar en un directorio temporal
        TEMP_DIR=$(mktemp -d)
        curl -o "${TEMP_DIR}/cloud-sql-proxy" "$PROXY_URL"
        chmod +x "${TEMP_DIR}/cloud-sql-proxy"
        
        # Intentar mover a /usr/local/bin, si falla usar ~/cloud-sql-proxy
        if sudo mv "${TEMP_DIR}/cloud-sql-proxy" /usr/local/bin/ 2>/dev/null; then
            PROXY_CMD="/usr/local/bin/cloud-sql-proxy"
        elif mv "${TEMP_DIR}/cloud-sql-proxy" "$HOME/cloud-sql-proxy" 2>/dev/null; then
            PROXY_CMD="$HOME/cloud-sql-proxy"
        else
            PROXY_CMD="${TEMP_DIR}/cloud-sql-proxy"
        fi
        
        rmdir "${TEMP_DIR}" 2>/dev/null || true
    fi
    
    CONNECTION_NAME=$(get_connection_name)
    
    # Detectar puerto disponible (5432 o 5433)
    PROXY_PORT=5432
    if lsof -Pi :5432 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  Puerto 5432 está en uso, usando puerto alternativo 5433"
        PROXY_PORT=5433
        if lsof -Pi :5433 -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo "⚠️  Puerto 5433 también está en uso, usando 5434"
            PROXY_PORT=5434
        fi
    fi
    
    echo "Iniciando Cloud SQL Proxy..."
    echo "Connection: ${CONNECTION_NAME}"
    echo "Puerto: ${PROXY_PORT}"
    echo ""
    
    # Obtener contraseña
    echo "Obteniendo contraseña de Secret Manager..."
    SECRET_NAME="${DATABASE//_/-}-db-password"
    PASSWORD=$(gcloud secrets versions access latest --secret="${SECRET_NAME}" 2>/dev/null || echo "")
    
    if [ -z "$PASSWORD" ]; then
        echo "⚠️  No se pudo obtener la contraseña automáticamente."
        echo "Ejecuta manualmente:"
        echo "  gcloud secrets versions access latest --secret=\"${SECRET_NAME}\""
        echo ""
        echo "Luego ejecuta:"
        echo "  PGPASSWORD=[contraseña] psql -h 127.0.0.1 -p ${PROXY_PORT} -U ${USER} -d ${DATABASE}"
    else
        echo "✅ Contraseña obtenida."
        echo ""
        
        # Limpiar procesos anteriores del proxy
        pkill -f "cloud-sql-proxy.*${CONNECTION_NAME}" 2>/dev/null || true
        sleep 1
        
        echo "Iniciando proxy en background..."
        echo "Usando: ${PROXY_CMD}"
        "${PROXY_CMD}" "${CONNECTION_NAME}" --port=${PROXY_PORT} > /tmp/cloud-sql-proxy.log 2>&1 &
        PROXY_PID=$!
        sleep 4
        
        # Verificar que el proxy está corriendo
        if ! ps -p $PROXY_PID > /dev/null 2>&1; then
            echo "❌ Error: El proxy no se inició correctamente"
            echo "Revisa los logs:"
            cat /tmp/cloud-sql-proxy.log | tail -5
            echo ""
            echo "💡 Alternativa: Usa gcloud sql connect directamente:"
            echo "   gcloud sql connect project-65436llm-postgres-instance --user=${USER} --database=${DATABASE}"
            return 1
        fi
        
        echo "✅ Proxy iniciado correctamente (PID: $PROXY_PID)"
        echo "Conectando a la base de datos..."
        echo ""
        PGPASSWORD="${PASSWORD}" psql -h 127.0.0.1 -p ${PROXY_PORT} -U ${USER} -d ${DATABASE}
        
        # Limpiar proxy al salir
        echo ""
        echo "Cerrando proxy..."
        kill $PROXY_PID 2>/dev/null || true
    fi
}

# Menú principal
show_menu() {
    echo "Selecciona un método de conexión:"
    echo ""
    echo "1) Cloud SQL Proxy (Recomendado para desarrollo local)"
    echo "2) Cloud Shell (Más fácil, sin instalación)"
    echo "3) gcloud CLI directo (requiere autorizar IP)"
    echo "4) Obtener contraseñas de Secret Manager"
    echo "5) Conexión automática con Proxy"
    echo ""
    read -p "Opción [1-5]: " option
    
    case $option in
        1) method_proxy ;;
        2) method_cloud_shell ;;
        3) method_gcloud ;;
        4) method_get_passwords ;;
        5) 
            read -p "Base de datos [auth_service]: " db
            read -p "Usuario [auth_service_user]: " user
            method_proxy_auto "${db:-auth_service}" "${user:-auth_service_user}"
            ;;
        *) echo "Opción inválida" ;;
    esac
}

# Si se pasan argumentos, ejecutar directamente
if [ $# -eq 0 ]; then
    show_menu
else
    case $1 in
        proxy) method_proxy ;;
        cloud-shell) method_cloud_shell ;;
        gcloud) method_gcloud ;;
        passwords) method_get_passwords ;;
        auto) method_proxy_auto $2 $3 ;;
        *) 
            echo "Uso: $0 [proxy|cloud-shell|gcloud|passwords|auto] [database] [usuario]"
            exit 1
            ;;
    esac
fi

