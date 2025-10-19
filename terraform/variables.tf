# Variables para configuración general
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "medisupply"
}

# Variables para ECS
variable "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  type        = string
  default     = "medisupply-cluster"
}

variable "ecs_service_name" {
  description = "Name of the ECS service"
  type        = string
  default     = "medisupply-service"
}

variable "container_name" {
  description = "Name of the container"
  type        = string
  default     = "medisupply-container"
}

variable "container_port" {
  description = "Port exposed by the container"
  type        = number
  default     = 8000
}

variable "app_count" {
  description = "Number of docker containers to run"
  type        = number
  default     = 2
}

variable "fargate_cpu" {
  description = "Fargate instance CPU units to provision (256 = 0.25 vCPU)"
  type        = number
  default     = 512
}

variable "fargate_memory" {
  description = "Fargate instance memory to provision (in MiB)"
  type        = number
  default     = 1024
}

# Variables para base de datos (opcional)
variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage"
  type        = number
  default     = 20
}

variable "db_engine_version" {
  description = "RDS engine version"
  type        = string
  default     = "13.7"
}

variable "db_name" {
  description = "RDS database name"
  type        = string
  default     = "medisupply"
}

variable "db_username" {
  description = "RDS database username"
  type        = string
  default     = "medisupply"
  sensitive   = true
}

variable "db_password" {
  description = "RDS database password"
  type        = string
  sensitive   = true
}

# Variables para Redis (opcional)
variable "redis_node_type" {
  description = "Redis node type"
  type        = string
  default     = "cache.t3.micro"
}

variable "redis_num_cache_nodes" {
  description = "Number of Redis cache nodes"
  type        = number
  default     = 1
}

# Variables para tags
variable "tags" {
  description = "A mapping of tags to assign to the resource"
  type        = map(string)
  default = {
    Project     = "medisupply"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}
