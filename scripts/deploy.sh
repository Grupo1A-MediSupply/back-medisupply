#!/bin/bash

# Script de despliegue para AWS ECS con Terraform
# Uso: ./scripts/deploy.sh [environment]

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅${NC} $1"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌${NC} $1"
}

# Variables
ENVIRONMENT=${1:-production}
TERRAFORM_DIR="terraform"
AWS_REGION="us-east-1"

# Verificar dependencias
check_dependencies() {
    log "Verificando dependencias..."
    
    if ! command -v terraform &> /dev/null; then
        error "Terraform no está instalado. Instálalo desde https://terraform.io"
        exit 1
    fi
    
    if ! command -v aws &> /dev/null; then
        error "AWS CLI no está instalado. Instálalo desde https://aws.amazon.com/cli/"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        error "Docker no está instalado. Instálalo desde https://docker.com"
        exit 1
    fi
    
    success "Todas las dependencias están instaladas"
}

# Verificar configuración AWS
check_aws_config() {
    log "Verificando configuración AWS..."
    
    if ! aws sts get-caller-identity &> /dev/null; then
        error "AWS no está configurado correctamente. Ejecuta 'aws configure'"
        exit 1
    fi
    
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    log "Usando cuenta AWS: $ACCOUNT_ID"
    success "AWS configurado correctamente"
}

# Construir y subir imágenes Docker
build_and_push_images() {
    log "Construyendo y subiendo imágenes Docker..."
    
    cd "$TERRAFORM_DIR"
    
    # Obtener URLs de ECR
    AUTH_REPO=$(terraform output -raw ecr_auth_service_url 2>/dev/null || echo "")
    PRODUCT_REPO=$(terraform output -raw ecr_product_service_url 2>/dev/null || echo "")
    
    if [ -z "$AUTH_REPO" ] || [ -z "$PRODUCT_REPO" ]; then
        warning "ECR repositories no encontrados. Ejecutando terraform apply primero..."
        terraform apply -auto-approve
        AUTH_REPO=$(terraform output -raw ecr_auth_service_url)
        PRODUCT_REPO=$(terraform output -raw ecr_product_service_url)
    fi
    
    cd ..
    
    # Login a ECR
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
    
    # Build y push Auth Service
    log "Construyendo Auth Service..."
    docker build -t $AUTH_REPO:latest -f apiMS/microservices/auth-service/Dockerfile apiMS/microservices/
    docker push $AUTH_REPO:latest
    
    # Build y push Product Service
    log "Construyendo Product Service..."
    docker build -t $PRODUCT_REPO:latest -f apiMS/microservices/product-service/Dockerfile apiMS/microservices/
    docker push $PRODUCT_REPO:latest
    
    success "Imágenes Docker construidas y subidas"
}

# Ejecutar Terraform
run_terraform() {
    log "Ejecutando Terraform..."
    
    cd "$TERRAFORM_DIR"
    
    # Inicializar Terraform
    log "Inicializando Terraform..."
    terraform init
    
    # Planificar cambios
    log "Planificando cambios..."
    terraform plan -out=tfplan
    
    # Aplicar cambios
    log "Aplicando cambios..."
    terraform apply -auto-approve tfplan
    
    # Mostrar outputs
    log "Outputs de Terraform:"
    terraform output
    
    cd ..
    
    success "Terraform aplicado correctamente"
}

# Actualizar servicio ECS
update_ecs_service() {
    log "Actualizando servicio ECS..."
    
    CLUSTER_NAME=$(cd $TERRAFORM_DIR && terraform output -raw ecs_cluster_name)
    SERVICE_NAME=$(cd $TERRAFORM_DIR && terraform output -raw ecs_service_name)
    
    # Forzar nuevo despliegue
    aws ecs update-service \
        --cluster $CLUSTER_NAME \
        --service $SERVICE_NAME \
        --force-new-deployment
    
    # Esperar a que el servicio se estabilice
    log "Esperando a que el servicio se estabilice..."
    aws ecs wait services-stable \
        --cluster $CLUSTER_NAME \
        --services $SERVICE_NAME
    
    success "Servicio ECS actualizado"
}

# Verificar salud del despliegue
check_deployment_health() {
    log "Verificando salud del despliegue..."
    
    cd "$TERRAFORM_DIR"
    SERVICE_URL=$(terraform output -raw ecs_service_url)
    cd ..
    
    # Esperar un poco para que el servicio esté completamente listo
    sleep 30
    
    # Verificar endpoint de salud
    if curl -f "$SERVICE_URL/health" &> /dev/null; then
        success "Despliegue saludable en: $SERVICE_URL"
    else
        warning "El servicio puede estar aún iniciando. URL: $SERVICE_URL"
    fi
}

# Función principal
main() {
    echo "🚀 Iniciando despliegue a AWS ECS"
    echo "=================================="
    echo "Entorno: $ENVIRONMENT"
    echo "Región: $AWS_REGION"
    echo "=================================="
    
    check_dependencies
    check_aws_config
    
    # Preguntar si continuar
    read -p "¿Continuar con el despliegue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "Despliegue cancelado"
        exit 0
    fi
    
    run_terraform
    build_and_push_images
    update_ecs_service
    check_deployment_health
    
    success "🎉 Despliegue completado exitosamente!"
    
    cd "$TERRAFORM_DIR"
    echo ""
    echo "📋 Información del despliegue:"
    echo "================================"
    terraform output
    cd ..
}

# Ejecutar función principal
main "$@"
