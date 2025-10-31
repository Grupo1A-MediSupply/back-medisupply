# ==============================================================================
# Variables de Terraform
# ==============================================================================

variable "project_id" {
  type        = string
  description = "ID del proyecto GCP"
}

variable "region" {
  description = "Región de GCP donde se desplegarán los recursos"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "Zona de GCP (opcional)"
  type        = string
  default     = "us-central1-a"
}

variable "secret_key" {
  description = "Secret key para JWT (generar con: openssl rand -hex 32)"
  type        = string
  sensitive   = true
}

variable "environment" {
  description = "Ambiente de despliegue (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "min_instances" {
  description = "Número mínimo de instancias de Cloud Run (0 = serverless, más económico)"
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Número máximo de instancias de Cloud Run"
  type        = number
  default     = 10
}

variable "cpu_limit" {
  description = "Límite de CPU por instancia (ej: '1', '2')"
  type        = string
  default     = "1"
}

variable "memory_limit" {
  description = "Límite de memoria por instancia (ej: '512Mi', '1Gi')"
  type        = string
  default     = "512Mi"
}

variable "db_tier" {
  description = "Tier de la instancia Cloud SQL (db-f1-micro es el más económico, ~$7/mes)"
  type        = string
  default     = "db-f1-micro"
}

variable "db_root_password" {
  description = "Contraseña del usuario root de PostgreSQL (generar con: openssl rand -base64 32)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "enable_cloud_sql" {
  description = "Habilitar Cloud SQL PostgreSQL (si es false, usa SQLite)"
  type        = bool
  default     = true
}

