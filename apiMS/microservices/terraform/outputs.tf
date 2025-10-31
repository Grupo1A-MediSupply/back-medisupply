# ==============================================================================
# Outputs de Terraform
# ==============================================================================

output "artifact_registry_url" {
  description = "URL del Artifact Registry"
  value       = google_artifact_registry_repository.docker_repo.name
}

output "auth_service_url" {
  description = "URL del Auth Service"
  value       = google_cloud_run_service.auth_service.status[0].url
}

output "product_service_url" {
  description = "URL del Product Service"
  value       = google_cloud_run_service.product_service.status[0].url
}

output "order_service_url" {
  description = "URL del Order Service"
  value       = google_cloud_run_service.order_service.status[0].url
}

output "logistics_service_url" {
  description = "URL del Logistics Service"
  value       = google_cloud_run_service.logistics_service.status[0].url
}

output "notifications_service_url" {
  description = "URL del Notifications Service"
  value       = google_cloud_run_service.notifications_service.status[0].url
}

output "services_info" {
  description = "Información de todos los servicios"
  value = {
    auth_service          = google_cloud_run_service.auth_service.status[0].url
    product_service       = google_cloud_run_service.product_service.status[0].url
    order_service         = google_cloud_run_service.order_service.status[0].url
    logistics_service     = google_cloud_run_service.logistics_service.status[0].url
    notifications_service = google_cloud_run_service.notifications_service.status[0].url
  }
}

