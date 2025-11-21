# Outputs para información importante después del despliegue

output "cloud_run_service_url" {
  description = "URL of the Cloud Run service"
  value       = google_cloud_run_v2_service.monolith.uri
}

output "cloud_run_service_name" {
  description = "Name of the Cloud Run service"
  value       = google_cloud_run_v2_service.monolith.name
}

output "cloud_run_service_location" {
  description = "Location of the Cloud Run service"
  value       = google_cloud_run_v2_service.monolith.location
}

output "artifact_registry_repository_url" {
  description = "URL of the Artifact Registry repository"
  value       = var.use_existing_artifact_registry ? "projects/${var.project_id}/locations/${var.region}/repositories/${var.artifact_registry_name}" : (length(google_artifact_registry_repository.monolith) > 0 ? google_artifact_registry_repository.monolith[0].name : "N/A")
}

output "artifact_registry_repository_id" {
  description = "ID of the Artifact Registry repository"
  value       = var.artifact_registry_name
}

output "service_account_email" {
  description = "Email of the Cloud Run service account"
  value       = var.service_account_email != "" ? var.service_account_email : (var.create_service_account ? google_service_account.cloud_run[0].email : "N/A - Service Account debe ser configurado manualmente")
}

output "cloud_sql_instance_name" {
  description = "Name of the Cloud SQL instance (if enabled)"
  value       = var.enable_cloud_sql ? google_sql_database_instance.main[0].name : null
}

output "cloud_sql_connection_name" {
  description = "Connection name of the Cloud SQL instance (if enabled)"
  value       = var.enable_cloud_sql ? google_sql_database_instance.main[0].connection_name : null
}

output "secret_key_secret_id" {
  description = "Secret Manager secret ID for SECRET_KEY"
  value       = local.secret_key_id
}

output "database_url_secret_id" {
  description = "Secret Manager secret ID for DATABASE_URL (if Cloud SQL enabled)"
  value       = local.database_url_secret_id
}
