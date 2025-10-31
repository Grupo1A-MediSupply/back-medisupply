# ==============================================================================
# Terraform Configuration para GCP - Microservicios MediSupply
# ==============================================================================
# Este archivo crea la infraestructura necesaria en GCP usando servicios
# gratuitos o muy económicos (Cloud Run, Artifact Registry, etc.)
# ==============================================================================

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }
  }

  # Backend opcional: descomentar si quieres usar Cloud Storage como backend
  # backend "gcs" {
  #   bucket = "medisupply-terraform-state"
  #   prefix = "terraform/state"
  # }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# ==============================================================================
# ARTIFACT REGISTRY - Almacenamiento de imágenes Docker
# ==============================================================================

resource "google_artifact_registry_repository" "docker_repo" {
  location      = var.region
  repository_id = "${var.project_id}-docker-repo"
  description   = "Repositorio Docker para microservicios MediSupply"
  format        = "DOCKER"
}

# ==============================================================================
# VERIFICACIÓN DE IMÁGENES - Asegurar que las imágenes existan antes de desplegar
# ==============================================================================

# Usar null_resource para verificar que Artifact Registry esté listo
resource "null_resource" "wait_for_registry" {
  depends_on = [google_artifact_registry_repository.docker_repo]
  
  triggers = {
    registry_id = google_artifact_registry_repository.docker_repo.repository_id
  }
}

# ==============================================================================
# CLOUD RUN SERVICES - Microservicios serverless
# ==============================================================================

# Auth Service
resource "google_cloud_run_service" "auth_service" {
  name     = "auth-service"
  location = var.region

  # Esperar a que el registro esté listo
  depends_on = [null_resource.wait_for_registry]

  template {
    spec {
      containers {
        # Usar el tag específico o latest según disponibilidad
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}/auth-service:latest"

        ports {
          container_port = 8001
        }

        env {
          name  = "ENVIRONMENT"
          value = "production"
        }
        env {
          name  = "DEBUG"
          value = "false"
        }
        env {
          name  = "AUTH_SERVICE_PORT"
          value = "8001"
        }
        env {
          name = "SECRET_KEY"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.secret_key.secret_id
              key  = "latest"
            }
          }
        }
        env {
          name  = "AUTH_DATABASE_URL"
          value = "sqlite:///./data/auth_service.db"
        }

        resources {
          limits = {
            cpu    = "1"
            memory = "512Mi"
          }
          requests = {
            cpu    = "100m"
            memory = "128Mi"
          }
        }
      }

      container_concurrency = 80
      timeout_seconds       = 300
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale"  = "0"
        "autoscaling.knative.dev/maxScale"  = "10"
        "run.googleapis.com/cpu-throttling" = "true"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Product Service
resource "google_cloud_run_service" "product_service" {
  name     = "product-service"
  location = var.region

  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}/product-service:latest"

        ports {
          container_port = 8002
        }

        env {
          name  = "ENVIRONMENT"
          value = "production"
        }
        env {
          name  = "DEBUG"
          value = "false"
        }
        env {
          name  = "PRODUCT_SERVICE_PORT"
          value = "8002"
        }
        env {
          name  = "PRODUCT_DATABASE_URL"
          value = "sqlite:///./data/product_service.db"
        }
        env {
          name  = "AUTH_SERVICE_URL"
          value = google_cloud_run_service.auth_service.status[0].url
        }

        resources {
          limits = {
            cpu    = "1"
            memory = "512Mi"
          }
          requests = {
            cpu    = "100m"
            memory = "128Mi"
          }
        }
      }

      container_concurrency = 80
      timeout_seconds       = 300
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale"  = "0"
        "autoscaling.knative.dev/maxScale"  = "10"
        "run.googleapis.com/cpu-throttling" = "true"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Order Service
resource "google_cloud_run_service" "order_service" {
  name     = "order-service"
  location = var.region

  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}/order-service:latest"

        ports {
          container_port = 8003
        }

        env {
          name  = "ENVIRONMENT"
          value = "production"
        }
        env {
          name  = "DEBUG"
          value = "false"
        }
        env {
          name  = "ORDER_SERVICE_PORT"
          value = "8003"
        }
        env {
          name  = "ORDER_DATABASE_URL"
          value = "sqlite:///./data/order_service.db"
        }
        env {
          name  = "PRODUCT_SERVICE_URL"
          value = google_cloud_run_service.product_service.status[0].url
        }
        env {
          name  = "AUTH_SERVICE_URL"
          value = google_cloud_run_service.auth_service.status[0].url
        }

        resources {
          limits = {
            cpu    = "1"
            memory = "512Mi"
          }
          requests = {
            cpu    = "100m"
            memory = "128Mi"
          }
        }
      }

      container_concurrency = 80
      timeout_seconds       = 300
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale"  = "0"
        "autoscaling.knative.dev/maxScale"  = "10"
        "run.googleapis.com/cpu-throttling" = "true"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Logistics Service
resource "google_cloud_run_service" "logistics_service" {
  name     = "logistics-service"
  location = var.region

  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}/logistics-service:latest"

        ports {
          container_port = 8004
        }

        env {
          name  = "ENVIRONMENT"
          value = "production"
        }
        env {
          name  = "DEBUG"
          value = "false"
        }
        env {
          name  = "LOGISTICS_SERVICE_PORT"
          value = "8004"
        }
        env {
          name  = "LOGISTICS_DATABASE_URL"
          value = "sqlite:///./data/logistics_service.db"
        }
        env {
          name  = "ORDER_SERVICE_URL"
          value = google_cloud_run_service.order_service.status[0].url
        }

        resources {
          limits = {
            cpu    = "1"
            memory = "512Mi"
          }
          requests = {
            cpu    = "100m"
            memory = "128Mi"
          }
        }
      }

      container_concurrency = 80
      timeout_seconds       = 300
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale"  = "0"
        "autoscaling.knative.dev/maxScale"  = "10"
        "run.googleapis.com/cpu-throttling" = "true"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Notifications Service
resource "google_cloud_run_service" "notifications_service" {
  name     = "notifications-service"
  location = var.region

  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}/notifications-service:latest"

        ports {
          container_port = 8007
        }

        env {
          name  = "ENVIRONMENT"
          value = "production"
        }
        env {
          name  = "DEBUG"
          value = "false"
        }
        env {
          name  = "NOTIFICATIONS_SERVICE_PORT"
          value = "8007"
        }
        env {
          name  = "NOTIFICATIONS_DATABASE_URL"
          value = "sqlite:///./data/notifications_service.db"
        }
        env {
          name  = "AUTH_SERVICE_URL"
          value = google_cloud_run_service.auth_service.status[0].url
        }

        resources {
          limits = {
            cpu    = "1"
            memory = "512Mi"
          }
          requests = {
            cpu    = "100m"
            memory = "128Mi"
          }
        }
      }

      container_concurrency = 80
      timeout_seconds       = 300
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale"  = "0"
        "autoscaling.knative.dev/maxScale"  = "10"
        "run.googleapis.com/cpu-throttling" = "true"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# ==============================================================================
# IAM - Permisos para Cloud Run (público invocable)
# ==============================================================================

resource "google_cloud_run_service_iam_member" "auth_service_public" {
  service  = google_cloud_run_service.auth_service.name
  location = google_cloud_run_service.auth_service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_service_iam_member" "product_service_public" {
  service  = google_cloud_run_service.product_service.name
  location = google_cloud_run_service.product_service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_service_iam_member" "order_service_public" {
  service  = google_cloud_run_service.order_service.name
  location = google_cloud_run_service.order_service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_service_iam_member" "logistics_service_public" {
  service  = google_cloud_run_service.logistics_service.name
  location = google_cloud_run_service.logistics_service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_service_iam_member" "notifications_service_public" {
  service  = google_cloud_run_service.notifications_service.name
  location = google_cloud_run_service.notifications_service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# ==============================================================================
# SECRET MANAGER - Almacenamiento seguro de secretos
# ==============================================================================

resource "google_secret_manager_secret" "secret_key" {
  secret_id = "auth-service-secret-key"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "secret_key" {
  secret      = google_secret_manager_secret.secret_key.id
  secret_data = var.secret_key
}

# ==============================================================================
# IAM - Permisos para Cloud Run acceder a Secret Manager
# ==============================================================================

data "google_project" "project" {
  project_id = var.project_id
}

# Permitir que Cloud Run acceda a Secret Manager
resource "google_project_iam_member" "cloud_run_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
}

