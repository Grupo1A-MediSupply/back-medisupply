#!/bin/bash

# Script para importar recursos existentes de AWS al estado de Terraform
# Uso: ./import-existing-resources.sh

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

echo "🔄 IMPORTANDO RECURSOS EXISTENTES DE AWS A TERRAFORM"
echo "=================================================="
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "main.tf" ]; then
    error "No se encontró main.tf. Ejecuta este script desde el directorio terraform/"
    exit 1
fi

# Inicializar Terraform si no está inicializado
log "Inicializando Terraform..."
terraform init

# Obtener IDs de recursos existentes
log "Obteniendo IDs de recursos existentes..."

# Load Balancer
ALB_ARN=$(aws elbv2 describe-load-balancers --names medisupply-alb --query 'LoadBalancers[0].LoadBalancerArn' --output text 2>/dev/null || echo "")
if [ "$ALB_ARN" != "" ] && [ "$ALB_ARN" != "None" ]; then
    log "Importando Load Balancer: $ALB_ARN"
    terraform import aws_lb.main "$ALB_ARN" || warning "No se pudo importar Load Balancer"
else
    warning "Load Balancer medisupply-alb no encontrado"
fi

# Target Group
TG_ARN=$(aws elbv2 describe-target-groups --names medisupply-tg --query 'TargetGroups[0].TargetGroupArn' --output text 2>/dev/null || echo "")
if [ "$TG_ARN" != "" ] && [ "$TG_ARN" != "None" ]; then
    log "Importando Target Group: $TG_ARN"
    terraform import aws_lb_target_group.main "$TG_ARN" || warning "No se pudo importar Target Group"
else
    warning "Target Group medisupply-tg no encontrado"
fi

# ECR Repositories
log "Importando ECR Repositories..."
terraform import aws_ecr_repository.auth_service medisupply-auth-service || warning "No se pudo importar ECR auth-service"
terraform import aws_ecr_repository.product_service medisupply-product-service || warning "No se pudo importar ECR product-service"

# IAM Roles
log "Importando IAM Roles..."
terraform import aws_iam_role.ecs_task_execution_role medisupply-ecs-task-execution-role || warning "No se pudo importar IAM role ecs_task_execution_role"
terraform import aws_iam_role.ecs_task_role medisupply-ecs-task-role || warning "No se pudo importar IAM role ecs_task_role"

# CloudWatch Log Group
log "Importando CloudWatch Log Group..."
terraform import aws_cloudwatch_log_group.main /ecs/medisupply || warning "No se pudo importar CloudWatch Log Group"

# VPC (si existe)
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=tag:Name,Values=medisupply-vpc" --query 'Vpcs[0].VpcId' --output text 2>/dev/null || echo "")
if [ "$VPC_ID" != "" ] && [ "$VPC_ID" != "None" ]; then
    log "Importando VPC: $VPC_ID"
    terraform import aws_vpc.main "$VPC_ID" || warning "No se pudo importar VPC"
else
    warning "VPC medisupply-vpc no encontrada"
fi

# Internet Gateway
IGW_ID=$(aws ec2 describe-internet-gateways --filters "Name=tag:Name,Values=medisupply-igw" --query 'InternetGateways[0].InternetGatewayId' --output text 2>/dev/null || echo "")
if [ "$IGW_ID" != "" ] && [ "$IGW_ID" != "None" ]; then
    log "Importando Internet Gateway: $IGW_ID"
    terraform import aws_internet_gateway.main "$IGW_ID" || warning "No se pudo importar Internet Gateway"
else
    warning "Internet Gateway medisupply-igw no encontrado"
fi

# ECS Cluster
CLUSTER_ARN=$(aws ecs describe-clusters --clusters medisupply-cluster --query 'clusters[0].clusterArn' --output text 2>/dev/null || echo "")
if [ "$CLUSTER_ARN" != "" ] && [ "$CLUSTER_ARN" != "None" ]; then
    log "Importando ECS Cluster: $CLUSTER_ARN"
    terraform import aws_ecs_cluster.main "$CLUSTER_ARN" || warning "No se pudo importar ECS Cluster"
else
    warning "ECS Cluster medisupply-cluster no encontrado"
fi

# Verificar estado después de la importación
log "Verificando estado de Terraform..."
terraform plan

success "Importación completada. Revisa el plan de Terraform para verificar que todo esté correcto."
echo ""
echo "📋 Próximos pasos:"
echo "1. Revisa el output de 'terraform plan'"
echo "2. Si todo se ve correcto, ejecuta 'terraform apply'"
echo "3. O ejecuta el pipeline de GitHub Actions nuevamente"
