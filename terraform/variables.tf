# Variables para configuración general
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "medisupply"
}

# Variables para Cloud Run
variable "service_name" {
  description = "Name of the Cloud Run service"
  type        = string
  default     = "medisupply-monolith"
}

variable "container_port" {
  description = "Port exposed by the container"
  type        = number
  default     = 8000
}

variable "min_instances" {
  description = "Minimum number of Cloud Run instances"
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum number of Cloud Run instances"
  type        = number
  default     = 10
}

variable "cpu_limit" {
  description = "CPU limit for Cloud Run service (e.g., '1', '2', '4')"
  type        = string
  default     = "2"
}

variable "memory_limit" {
  description = "Memory limit for Cloud Run service (e.g., '512Mi', '1Gi', '2Gi')"
  type        = string
  default     = "2Gi"
}

variable "image_tag" {
  description = "Docker image tag to deploy"
  type        = string
  default     = "latest"
}

variable "allow_unauthenticated" {
  description = "Allow unauthenticated access to Cloud Run service"
  type        = bool
  default     = true
}

# Variables para Artifact Registry
variable "artifact_registry_name" {
  description = "Name of the Artifact Registry repository"
  type        = string
  default     = "medisupply-docker-repo"
}

variable "use_existing_artifact_registry" {
  description = "Use existing Artifact Registry repository instead of creating a new one"
  type        = bool
  default     = true
}

variable "use_existing_secrets" {
  description = "Use existing Secret Manager secrets instead of creating new ones"
  type        = bool
  default     = true
}

variable "secret_key" {
  description = "Secret key value for JWT (will be stored in Secret Manager)"
  type        = string
  sensitive   = true
  default     = ""
}

# Variables para Cloud SQL (opcional)
variable "enable_cloud_sql" {
  description = "Enable Cloud SQL instance"
  type        = bool
  default     = false
}

variable "db_version" {
  description = "Cloud SQL database version"
  type        = string
  default     = "POSTGRES_15"
}

variable "db_tier" {
  description = "Cloud SQL instance tier"
  type        = string
  default     = "db-f1-micro"
}

variable "db_availability_type" {
  description = "Cloud SQL availability type (ZONAL or REGIONAL)"
  type        = string
  default     = "ZONAL"
}

variable "db_disk_size" {
  description = "Cloud SQL disk size in GB"
  type        = number
  default     = 20
}

variable "db_name" {
  description = "Cloud SQL database name"
  type        = string
  default     = "medisupply"
}

variable "db_user" {
  description = "Cloud SQL database user"
  type        = string
  default     = "medisupply"
}

variable "db_password" {
  description = "Cloud SQL database password"
  type        = string
  sensitive   = true
  default     = ""
}

# Variables para Service Account
variable "create_service_account" {
  description = "Create a new service account (if false, use existing service_account_email)"
  type        = bool
  default     = true
}

variable "service_account_email" {
  description = "Email of existing service account to use (if create_service_account is false)"
  type        = string
  default     = ""
}

# Variables para tags/labels
variable "labels" {
  description = "Labels to apply to resources"
  type        = map(string)
  default = {
    project     = "medisupply"
    environment = "production"
    managed_by  = "terraform"
  }
}
