#!/bin/bash

# Script para importar TODOS los recursos existentes de AWS a Terraform
# Ejecutar desde el directorio 'terraform/'

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║            🔄 IMPORTANDO TODOS LOS RECURSOS EXISTENTES       ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Configurar AWS CLI
AWS_REGION="us-east-1"
echo "Configurando AWS CLI para la región: $AWS_REGION"
export AWS_DEFAULT_REGION=$AWS_REGION

# VPC ID específico
VPC_ID="vpc-05119ba31240eb9bd"
echo "Usando VPC ID: $VPC_ID"

# --- 1. ECR Repositories ---
echo "📦 Importando ECR Repositories..."
for service in auth-service product-service; do
    REPO_NAME="medisupply-$service"
    echo "Intentando importar ECR Repository: $REPO_NAME"
    aws ecr describe-repositories --repository-names $REPO_NAME > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        terraform import aws_ecr_repository.$service $REPO_NAME
        if [ $? -eq 0 ]; then
            echo "✅ ECR Repository $REPO_NAME importado exitosamente."
        else
            echo "❌ Error al importar ECR Repository $REPO_NAME."
        fi
    else
        echo "⚠️ ECR Repository $REPO_NAME no encontrado."
    fi
done

# --- 2. IAM Roles ---
echo "🔐 Importando IAM Roles..."
ROLES=(
    "ecs_task_execution_role:medisupply-ecs-task-execution-role"
    "ecs_task_role:medisupply-ecs-task-role"
)
for role_map in "${ROLES[@]}"; do
    TF_RESOURCE=$(echo $role_map | cut -d':' -f1)
    ROLE_NAME=$(echo $role_map | cut -d':' -f2)
    echo "Intentando importar IAM Role: $ROLE_NAME"
    aws iam get-role --role-name $ROLE_NAME > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        terraform import aws_iam_role.$TF_RESOURCE $ROLE_NAME
        if [ $? -eq 0 ]; then
            echo "✅ IAM Role $ROLE_NAME importado exitosamente."
        else
            echo "❌ Error al importar IAM Role $ROLE_NAME."
        fi
    else
        echo "⚠️ IAM Role $ROLE_NAME no encontrado."
    fi
done

# --- 3. CloudWatch Log Group ---
echo "📊 Importando CloudWatch Log Group..."
LOG_GROUP_NAME="/ecs/medisupply"
echo "Intentando importar CloudWatch Log Group: $LOG_GROUP_NAME"
aws logs describe-log-groups --log-group-name-prefix $LOG_GROUP_NAME > /dev/null 2>&1
if [ $? -eq 0 ]; then
    terraform import aws_cloudwatch_log_group.main $LOG_GROUP_NAME
    if [ $? -eq 0 ]; then
        echo "✅ CloudWatch Log Group $LOG_GROUP_NAME importado exitosamente."
    else
        echo "❌ Error al importar CloudWatch Log Group $LOG_GROUP_NAME."
    fi
else
    echo "⚠️ CloudWatch Log Group $LOG_GROUP_NAME no encontrado."
fi

# --- 4. Load Balancer ---
echo "⚖️ Importando Application Load Balancer..."
ALB_ARN=$(aws elbv2 describe-load-balancers --names medisupply-alb --query 'LoadBalancers[0].LoadBalancerArn' --output text 2>/dev/null || echo "")
if [ -n "$ALB_ARN" ] && [ "$ALB_ARN" != "None" ]; then
    echo "Intentando importar ALB: $ALB_ARN"
    terraform import aws_lb.main $ALB_ARN
    if [ $? -eq 0 ]; then
        echo "✅ ALB importado exitosamente."
    else
        echo "❌ Error al importar ALB."
    fi
else
    echo "⚠️ ALB medisupply-alb no encontrado."
fi

# --- 5. Target Group ---
echo "🎯 Importando Target Group..."
TG_ARN=$(aws elbv2 describe-target-groups --names medisupply-tg --query 'TargetGroups[0].TargetGroupArn' --output text 2>/dev/null || echo "")
if [ -n "$TG_ARN" ] && [ "$TG_ARN" != "None" ]; then
    echo "Intentando importar Target Group: $TG_ARN"
    terraform import aws_lb_target_group.main $TG_ARN
    if [ $? -eq 0 ]; then
        echo "✅ Target Group importado exitosamente."
    else
        echo "❌ Error al importar Target Group."
    fi
else
    echo "⚠️ Target Group medisupply-tg no encontrado."
fi

# --- 6. Route Table Associations ---
echo "🛣️ Importando Route Table Associations..."
# Obtener la route table pública
PUBLIC_RT_ID=$(aws ec2 describe-route-tables --filters "Name=vpc-id,Values=$VPC_ID" "Name=tag:Name,Values=medisupply-public-rt" --query 'RouteTables[0].RouteTableId' --output text 2>/dev/null || echo "")
if [ -n "$PUBLIC_RT_ID" ] && [ "$PUBLIC_RT_ID" != "None" ]; then
    echo "Route Table Pública encontrada: $PUBLIC_RT_ID"
    
    # Obtener las subnets públicas
    PUBLIC_SUBNET_1="subnet-0adf58bad0bee883a"
    PUBLIC_SUBNET_2="subnet-0eb32061dde9cae3f"
    
    # Importar asociaciones
    for i in 0 1; do
        SUBNET_ID=$([ $i -eq 0 ] && echo $PUBLIC_SUBNET_1 || echo $PUBLIC_SUBNET_2)
        echo "Intentando importar asociación para subnet $SUBNET_ID"
        terraform import "aws_route_table_association.public[$i]" "$SUBNET_ID/$PUBLIC_RT_ID"
        if [ $? -eq 0 ]; then
            echo "✅ Asociación $i importada exitosamente."
        else
            echo "❌ Error al importar asociación $i."
        fi
    done
else
    echo "⚠️ Route Table Pública no encontrada."
fi

# --- 7. Security Groups ---
echo "🔒 Importando Security Groups..."
# ALB Security Group
ALB_SG_ID=$(aws ec2 describe-security-groups --filters "Name=vpc-id,Values=$VPC_ID" "Name=group-name,Values=medisupply-alb-sg" --query 'SecurityGroups[0].GroupId' --output text 2>/dev/null || echo "")
if [ -n "$ALB_SG_ID" ] && [ "$ALB_SG_ID" != "None" ]; then
    terraform import aws_security_group.alb $ALB_SG_ID
    echo "✅ ALB Security Group importado: $ALB_SG_ID"
fi

# ECS Tasks Security Group
ECS_SG_ID=$(aws ec2 describe-security-groups --filters "Name=vpc-id,Values=$VPC_ID" "Name=group-name,Values=medisupply-ecs-tasks-sg" --query 'SecurityGroups[0].GroupId' --output text 2>/dev/null || echo "")
if [ -n "$ECS_SG_ID" ] && [ "$ECS_SG_ID" != "None" ]; then
    terraform import aws_security_group.ecs_tasks $ECS_SG_ID
    echo "✅ ECS Tasks Security Group importado: $ECS_SG_ID"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║            ✅ IMPORTACIÓN DE RECURSOS COMPLETADA             ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo "Ahora puedes ejecutar 'terraform plan' para verificar el estado."
