#!/bin/bash

# ==============================================================================
# Script para mostrar recursos desplegados en GCP, estado y costos estimados
# ==============================================================================

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Obtener proyecto y región desde Terraform o configuración
PROJECT_ID=$(cd "$(dirname "$0")" && terraform output -raw project_id 2>/dev/null || gcloud config get-value project 2>/dev/null || echo "")
REGION=$(cd "$(dirname "$0")" && terraform output -raw region 2>/dev/null || echo "us-central1")

# Si PROJECT_ID es un número (Project Number), convertir a Project ID
if [[ "$PROJECT_ID" =~ ^[0-9]+$ ]]; then
    echo -e "${YELLOW}⚠️  Detectado Project Number, convirtiendo a Project ID...${NC}"
    PROJECT_ID=$(gcloud projects describe "$PROJECT_ID" --format="value(projectId)" 2>/dev/null || echo "$PROJECT_ID")
fi

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: No se pudo determinar el PROJECT_ID${NC}"
    exit 1
fi

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}     📊 INFRAESTRUCTURA DESPLEGADA EN GCP${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📋 PROYECTO:${NC} $PROJECT_ID"
echo -e "${BLUE}📍 REGIÓN:${NC} $REGION"
echo ""

# Variables para costo total
TOTAL_COST=0
CLOUD_RUN_COST=0
CLOUD_SQL_COST=0
ARTIFACT_REGISTRY_COST=0
SECRET_MANAGER_COST=0

# ==============================================================================
# 1. CLOUD RUN SERVICES
# ==============================================================================

echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}1️⃣  CLOUD RUN SERVICES${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""

CLOUD_RUN_COUNT=0
CLOUD_RUN_ACTIVE=0

SERVICES=$(gcloud run services list --region="$REGION" --project="$PROJECT_ID" --format="value(metadata.name)" 2>/dev/null || echo "")

if [ -z "$SERVICES" ]; then
    echo -e "${YELLOW}⚠️  No hay servicios Cloud Run desplegados${NC}"
    echo ""
else
    while IFS= read -r service; do
        if [ ! -z "$service" ]; then
            CLOUD_RUN_COUNT=$((CLOUD_RUN_COUNT + 1))
            
            # Obtener detalles del servicio
            URL=$(gcloud run services describe "$service" --region="$REGION" --project="$PROJECT_ID" --format="value(status.url)" 2>/dev/null || echo "")
            STATUS=$(gcloud run services describe "$service" --region="$REGION" --project="$PROJECT_ID" --format="value(status.conditions[0].status)" 2>/dev/null || echo "")
            
            # Obtener configuración de recursos
            CPU_LIMIT=$(gcloud run services describe "$service" --region="$REGION" --project="$PROJECT_ID" --format="value(spec.template.spec.containers[0].resources.limits.cpu)" 2>/dev/null || echo "1")
            MEMORY_LIMIT=$(gcloud run services describe "$service" --region="$REGION" --project="$PROJECT_ID" --format="value(spec.template.spec.containers[0].resources.limits.memory)" 2>/dev/null || echo "512Mi")
            MIN_INSTANCES=$(gcloud run services describe "$service" --region="$REGION" --project="$PROJECT_ID" --format="value(metadata.annotations.autoscaling\.knative\.dev/minScale)" 2>/dev/null || echo "0")
            MAX_INSTANCES=$(gcloud run services describe "$service" --region="$REGION" --project="$PROJECT_ID" --format="value(metadata.annotations.autoscaling\.knative\.dev/maxScale)" 2>/dev/null || echo "10")
            
            if [ "$STATUS" = "True" ]; then
                CLOUD_RUN_ACTIVE=$((CLOUD_RUN_ACTIVE + 1))
                echo -e "${GREEN}✅ $service${NC}"
            else
                echo -e "${RED}❌ $service${NC}"
            fi
            
            echo -e "   URL: $URL"
            echo -e "   Estado: $STATUS"
            echo -e "   CPU: $CPU_LIMIT"
            echo -e "   Memoria: $MEMORY_LIMIT"
            echo -e "   Instancias: $MIN_INSTANCES - $MAX_INSTANCES"
            echo ""
            
            # Calcular costo aproximado (Cloud Run cobra por uso, asumimos 0.001$ por request + costo de recursos)
            # Estimación: ~$0.40/mes por servicio en tier mínimo con mínimo uso
            SERVICE_COST=0.40
            CLOUD_RUN_COST=$(echo "$CLOUD_RUN_COST + $SERVICE_COST" | bc)
        fi
    done <<< "$SERVICES"
    
    echo -e "${BLUE}📊 Total:${NC} $CLOUD_RUN_COUNT servicios ($CLOUD_RUN_ACTIVE activos)"
    echo -e "${BLUE}💰 Costo estimado:${NC} \$$(echo "scale=2; $CLOUD_RUN_COST" | bc)/mes"
    echo ""
fi

TOTAL_COST=$(echo "$TOTAL_COST + $CLOUD_RUN_COST" | bc)

# ==============================================================================
# 2. CLOUD SQL INSTANCES
# ==============================================================================

echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}2️⃣  CLOUD SQL INSTANCES${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""

CLOUD_SQL_COUNT=0

# Habilitar API si es necesario (sin prompts)
gcloud services enable sqladmin.googleapis.com --project="$PROJECT_ID" 2>/dev/null || true

SQL_INSTANCES=$(gcloud sql instances list --project="$PROJECT_ID" --format="value(name)" 2>/dev/null || echo "")

if [ -z "$SQL_INSTANCES" ]; then
    echo -e "${YELLOW}⚠️  No hay instancias Cloud SQL desplegadas${NC}"
    echo ""
else
    while IFS= read -r instance; do
        if [ ! -z "$instance" ]; then
            CLOUD_SQL_COUNT=$((CLOUD_SQL_COUNT + 1))
            
            # Obtener detalles de la instancia
            DB_VERSION=$(gcloud sql instances describe "$instance" --project="$PROJECT_ID" --format="value(databaseVersion)" 2>/dev/null || echo "")
            TIER=$(gcloud sql instances describe "$instance" --project="$PROJECT_ID" --format="value(settings.tier)" 2>/dev/null || echo "")
            DISK_SIZE=$(gcloud sql instances describe "$instance" --project="$PROJECT_ID" --format="value(settings.dataDiskSizeGb)" 2>/dev/null || echo "20")
            STATE=$(gcloud sql instances describe "$instance" --project="$PROJECT_ID" --format="value(state)" 2>/dev/null || echo "")
            
            echo -e "${GREEN}✅ $instance${NC}"
            echo -e "   Versión: $DB_VERSION"
            echo -e "   Tier: $TIER"
            echo -e "   Disco: ${DISK_SIZE}GB"
            echo -e "   Estado: $STATE"
            echo ""
            
            # Calcular costo aproximado según tier
            case "$TIER" in
                db-f1-micro)
                    INSTANCE_COST=7.48  # ~$7.48/mes
                    ;;
                db-f1-small)
                    INSTANCE_COST=12.81  # ~$12.81/mes
                    ;;
                db-g1-small)
                    INSTANCE_COST=25.60  # ~$25.60/mes
                    ;;
                *)
                    INSTANCE_COST=7.48  # Default a micro
                    ;;
            esac
            
            # Costo de disco: ~$0.17/GB/mes
            DISK_COST=$(echo "scale=2; $DISK_SIZE * 0.17" | bc)
            
            INSTANCE_TOTAL_COST=$(echo "scale=2; $INSTANCE_COST + $DISK_COST" | bc)
            CLOUD_SQL_COST=$(echo "scale=2; $CLOUD_SQL_COST + $INSTANCE_TOTAL_COST" | bc)
            
            echo -e "   ${BLUE}💰 Costo estimado:${NC} \$$INSTANCE_TOTAL_COST/mes"
            echo ""
        fi
    done <<< "$SQL_INSTANCES"
    
    echo -e "${BLUE}📊 Total:${NC} $CLOUD_SQL_COUNT instancias"
    echo -e "${BLUE}💰 Costo total estimado:${NC} \$$(echo "scale=2; $CLOUD_SQL_COST" | bc)/mes"
    echo ""
fi

TOTAL_COST=$(echo "scale=2; $TOTAL_COST + $CLOUD_SQL_COST" | bc)

# ==============================================================================
# 3. ARTIFACT REGISTRY
# ==============================================================================

echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}3️⃣  ARTIFACT REGISTRY${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""

REPO="${PROJECT_ID}-docker-repo"
REPO_EXISTS=$(gcloud artifacts repositories describe "$REPO" --location="$REGION" --project="$PROJECT_ID" --format="value(name)" 2>/dev/null || echo "")

if [ -z "$REPO_EXISTS" ]; then
    echo -e "${YELLOW}⚠️  No hay repositorio Artifact Registry${NC}"
    echo ""
else
    echo -e "${GREEN}✅ Repositorio: $REPO${NC}"
    echo -e "   Ubicación: $REGION"
    echo ""
    
    echo -e "${BLUE}📷 Imágenes Docker:${NC}"
    echo ""
    
    TOTAL_IMAGES=0
    TOTAL_STORAGE_GB=0
    
    for service in auth-service product-service order-service logistics-service notifications-service; do
        IMAGE_COUNT=$(gcloud artifacts docker images list "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/$service" --format="value(package)" 2>/dev/null | sort -u | wc -l | tr -d ' ' || echo "0")
        
        if [ "$IMAGE_COUNT" -gt 0 ]; then
            TOTAL_IMAGES=$((TOTAL_IMAGES + IMAGE_COUNT))
            # Obtener tamaño de la última imagen
            LATEST_IMAGE_SIZE=$(gcloud artifacts docker images list "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/$service" --format="value(sizeBytes)" --sort-by=~create_time --limit=1 2>/dev/null || echo "0")
            if [ "$LATEST_IMAGE_SIZE" != "0" ] && [ ! -z "$LATEST_IMAGE_SIZE" ]; then
                # Convertir bytes a GB
                IMAGE_SIZE_GB=$(echo "scale=4; $LATEST_IMAGE_SIZE / 1073741824" | bc)
                TOTAL_STORAGE_GB=$(echo "scale=4; $TOTAL_STORAGE_GB + $IMAGE_SIZE_GB" | bc)
            fi
            echo -e "   • $service: $IMAGE_COUNT imágenes"
        fi
    done
    
    echo ""
    echo -e "${BLUE}📊 Total:${NC} $TOTAL_IMAGES imágenes (~$(echo "scale=2; $TOTAL_STORAGE_GB" | bc) GB)"
    
    # Costo de Artifact Registry: primeros 50GB gratuitos, luego $0.10/GB/mes
    if (( $(echo "$TOTAL_STORAGE_GB > 50" | bc -l) )); then
        STORAGE_COST=$(echo "scale=2; ($TOTAL_STORAGE_GB - 50) * 0.10" | bc)
    else
        STORAGE_COST=0
    fi
    
    ARTIFACT_REGISTRY_COST=$STORAGE_COST
    echo -e "${BLUE}💰 Costo estimado:${NC} \$$(echo "scale=2; $ARTIFACT_REGISTRY_COST" | bc)/mes (primeros 50GB gratuitos)"
    echo ""
fi

TOTAL_COST=$(echo "scale=2; $TOTAL_COST + $ARTIFACT_REGISTRY_COST" | bc)

# ==============================================================================
# 4. SECRET MANAGER
# ==============================================================================

echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}4️⃣  SECRET MANAGER${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""

SECRET_COUNT=$(gcloud secrets list --project="$PROJECT_ID" --format="value(name)" 2>/dev/null | wc -l | tr -d ' ' || echo "0")

if [ "$SECRET_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  No hay secretos en Secret Manager${NC}"
    echo ""
else
    echo -e "${GREEN}✅ Secretos almacenados: $SECRET_COUNT${NC}"
    echo ""
    gcloud secrets list --project="$PROJECT_ID" --format="table(name,createTime)" 2>/dev/null || echo ""
    echo ""
    
    # Secret Manager: $0.06/secreto/mes
    SECRET_MANAGER_COST=$(echo "scale=2; $SECRET_COUNT * 0.06" | bc)
    echo -e "${BLUE}💰 Costo estimado:${NC} \$$(echo "scale=2; $SECRET_MANAGER_COST" | bc)/mes"
    echo ""
fi

TOTAL_COST=$(echo "scale=2; $TOTAL_COST + $SECRET_MANAGER_COST" | bc)

# ==============================================================================
# 5. TERRAFORM STATE
# ==============================================================================

echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}5️⃣  TERRAFORM STATE${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""

TERRAFORM_RESOURCES=$(cd "$(dirname "$0")" && terraform state list 2>/dev/null | wc -l | tr -d ' ' || echo "0")

echo -e "${BLUE}📊 Recursos gestionados:${NC} $TERRAFORM_RESOURCES"
echo ""

# Mostrar desglose
if [ "$TERRAFORM_RESOURCES" -gt 0 ]; then
    echo -e "${BLUE}Desglose:${NC}"
    echo -e "   • Cloud Run Services: $(cd "$(dirname "$0")" && terraform state list 2>/dev/null | grep -c cloud_run_service || echo "0")"
    echo -e "   • IAM Members: $(cd "$(dirname "$0")" && terraform state list 2>/dev/null | grep -c iam_member || echo "0")"
    echo -e "   • Cloud SQL: $(cd "$(dirname "$0")" && terraform state list 2>/dev/null | grep -c sql || echo "0")"
    echo -e "   • Secret Manager: $(cd "$(dirname "$0")" && terraform state list 2>/dev/null | grep -c secret_manager || echo "0")"
    echo -e "   • Artifact Registry: $(cd "$(dirname "$0")" && terraform state list 2>/dev/null | grep -c artifact_registry || echo "0")"
    echo ""
fi

# ==============================================================================
# RESUMEN FINAL
# ==============================================================================

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}          💰 RESUMEN DE COSTOS${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${BLUE}Servicios Cloud Run:${NC} \$$(echo "scale=2; $CLOUD_RUN_COST" | bc)/mes ($CLOUD_RUN_ACTIVE/$CLOUD_RUN_COUNT activos)"
echo -e "${BLUE}Cloud SQL:${NC} \$$(echo "scale=2; $CLOUD_SQL_COST" | bc)/mes"
echo -e "${BLUE}Artifact Registry:${NC} \$$(echo "scale=2; $ARTIFACT_REGISTRY_COST" | bc)/mes"
echo -e "${BLUE}Secret Manager:${NC} \$$(echo "scale=2; $SECRET_MANAGER_COST" | bc)/mes"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}💰 COSTO TOTAL ESTIMADO:${NC} \$$(echo "scale=2; $TOTAL_COST" | bc)/mes"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${YELLOW}ℹ️  Nota: Los costos son estimaciones basadas en configuración estática.${NC}"
echo -e "${YELLOW}   Los costos reales pueden variar según el uso (requests, tráfico, etc.).${NC}"
echo ""

