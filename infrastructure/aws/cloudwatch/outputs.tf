# ============================================================
# CloudWatch Outputs
# AI Resume Screening & Interview System
# ============================================================

# ------------------------------------------------------------
# Log Group Outputs
# ------------------------------------------------------------

output "backend_log_group_name" {
  description = "CloudWatch log group name for the backend"
  value       = aws_cloudwatch_log_group.backend.name
}

output "backend_log_group_arn" {
  description = "CloudWatch log group ARN for the backend"
  value       = aws_cloudwatch_log_group.backend.arn
}

output "frontend_log_group_name" {
  description = "CloudWatch log group name for the frontend"
  value       = aws_cloudwatch_log_group.frontend.name
}

output "frontend_log_group_arn" {
  description = "CloudWatch log group ARN for the frontend"
  value       = aws_cloudwatch_log_group.frontend.arn
}

output "worker_log_group_name" {
  description = "CloudWatch log group name for the worker"
  value       = aws_cloudwatch_log_group.worker.name
}

output "worker_log_group_arn" {
  description = "CloudWatch log group ARN for the worker"
  value       = aws_cloudwatch_log_group.worker.arn
}

output "celery_log_group_name" {
  description = "CloudWatch log group name for Celery"
  value       = aws_cloudwatch_log_group.celery.name
}

output "celery_log_group_arn" {
  description = "CloudWatch log group ARN for Celery"
  value       = aws_cloudwatch_log_group.celery.arn
}

output "ai_processing_log_group_name" {
  description = "CloudWatch log group name for AI processing"
  value       = aws_cloudwatch_log_group.ai_processing.name
}

output "ai_processing_log_group_arn" {
  description = "CloudWatch log group ARN for AI processing"
  value       = aws_cloudwatch_log_group.ai_processing.arn
}

output "interview_engine_log_group_name" {
  description = "CloudWatch log group name for the interview engine"
  value       = aws_cloudwatch_log_group.interview_engine.name
}

output "interview_engine_log_group_arn" {
  description = "CloudWatch log group ARN for the interview engine"
  value       = aws_cloudwatch_log_group.interview_engine.arn
}

output "application_log_group_name" {
  description = "CloudWatch log group name for the application"
  value       = aws_cloudwatch_log_group.application.name
}

output "application_log_group_arn" {
  description = "CloudWatch log group ARN for the application"
  value       = aws_cloudwatch_log_group.application.arn
}

output "nginx_log_group_name" {
  description = "CloudWatch log group name for Nginx"
  value       = aws_cloudwatch_log_group.nginx.name
}

output "nginx_log_group_arn" {
  description = "CloudWatch log group ARN for Nginx"
  value       = aws_cloudwatch_log_group.nginx.arn
}

output "database_log_group_name" {
  description = "CloudWatch log group name for database logs"
  value       = aws_cloudwatch_log_group.database.name
}

output "database_log_group_arn" {
  description = "CloudWatch log group ARN for database logs"
  value       = aws_cloudwatch_log_group.database.arn
}

output "audit_log_group_name" {
  description = "CloudWatch log group name for audit and security logs"
  value       = aws_cloudwatch_log_group.audit.name
}

output "audit_log_group_arn" {
  description = "CloudWatch log group ARN for audit and security logs"
  value       = aws_cloudwatch_log_group.audit.arn
}

output "errors_log_group_name" {
  description = "CloudWatch log group name for centralized errors"
  value       = aws_cloudwatch_log_group.errors.name
}

output "errors_log_group_arn" {
  description = "CloudWatch log group ARN for centralized errors"
  value       = aws_cloudwatch_log_group.errors.arn
}

# ------------------------------------------------------------
# All Log Groups
# ------------------------------------------------------------

output "log_groups" {
  description = "All CloudWatch log group names"
  value = {
    backend          = aws_cloudwatch_log_group.backend.name
    frontend         = aws_cloudwatch_log_group.frontend.name
    worker           = aws_cloudwatch_log_group.worker.name
    celery           = aws_cloudwatch_log_group.celery.name
    ai_processing    = aws_cloudwatch_log_group.ai_processing.name
    interview_engine = aws_cloudwatch_log_group.interview_engine.name
    application      = aws_cloudwatch_log_group.application.name
    nginx             = aws_cloudwatch_log_group.nginx.name
    database          = aws_cloudwatch_log_group.database.name
    audit             = aws_cloudwatch_log_group.audit.name
    errors            = aws_cloudwatch_log_group.errors.name
  }
}

# ------------------------------------------------------------
# Metric Namespaces
# ------------------------------------------------------------

output "application_metric_namespace" {
  description = "CloudWatch namespace for application metrics"
  value       = local.metric_namespace
}

output "ai_metric_namespace" {
  description = "CloudWatch namespace for AI metrics"
  value       = local.ai_metric_namespace
}

output "interview_metric_namespace" {
  description = "CloudWatch namespace for interview metrics"
  value       = local.interview_metric_namespace
}

output "celery_metric_namespace" {
  description = "CloudWatch namespace for Celery metrics"
  value       = local.celery_metric_namespace
}

output "database_metric_namespace" {
  description = "CloudWatch namespace for database metrics"
  value       = local.database_metric_namespace
}

output "security_metric_namespace" {
  description = "CloudWatch namespace for security metrics"
  value       = local.security_metric_namespace
}

# ------------------------------------------------------------
# Metric Filter Outputs
# ------------------------------------------------------------

output "metric_filters" {
  description = "CloudWatch metric filter names"

  value = {
    backend_errors            = aws_cloudwatch_log_metric_filter.backend_errors.name
    application_errors       = aws_cloudwatch_log_metric_filter.application_errors.name
    ai_processing_errors     = aws_cloudwatch_log_metric_filter.ai_processing_errors.name
    interview_errors         = aws_cloudwatch_log_metric_filter.interview_errors.name
    authentication_failures = aws_cloudwatch_log_metric_filter.authentication_failures.name
    resume_processing        = aws_cloudwatch_log_metric_filter.resume_processing.name
    interview_sessions       = aws_cloudwatch_log_metric_filter.interview_sessions.name
    api_requests             = aws_cloudwatch_log_metric_filter.api_requests.name
    http_5xx                 = aws_cloudwatch_log_metric_filter.http_5xx.name
    celery_failures          = aws_cloudwatch_log_metric_filter.celery_failures.name
    celery_completed         = aws_cloudwatch_log_metric_filter.celery_completed.name
    database_errors          = aws_cloudwatch_log_metric_filter.database_errors.name
    security_events          = aws_cloudwatch_log_metric_filter.security_events.name
    resume_uploads           = aws_cloudwatch_log_metric_filter.resume_uploads.name
    candidate_ranking        = aws_cloudwatch_log_metric_filter.candidate_ranking.name
    resume_matching          = aws_cloudwatch_log_metric_filter.resume_matching.name
    ats_scoring              = aws_cloudwatch_log_metric_filter.ats_scoring.name
  }
}

# ------------------------------------------------------------
# Retention
# ------------------------------------------------------------

output "log_retention_days" {
  description = "CloudWatch log retention period"
  value       = var.log_retention_days
}# ============================================================
# CloudWatch Outputs
# AI Resume Screening & Interview System
# ============================================================

# ------------------------------------------------------------
# Log Group Outputs
# ------------------------------------------------------------

output "backend_log_group_name" {
  description = "CloudWatch log group name for the backend"
  value       = aws_cloudwatch_log_group.backend.name
}

output "backend_log_group_arn" {
  description = "CloudWatch log group ARN for the backend"
  value       = aws_cloudwatch_log_group.backend.arn
}

output "frontend_log_group_name" {
  description = "CloudWatch log group name for the frontend"
  value       = aws_cloudwatch_log_group.frontend.name
}

output "frontend_log_group_arn" {
  description = "CloudWatch log group ARN for the frontend"
  value       = aws_cloudwatch_log_group.frontend.arn
}

output "worker_log_group_name" {
  description = "CloudWatch log group name for the worker"
  value       = aws_cloudwatch_log_group.worker.name
}

output "worker_log_group_arn" {
  description = "CloudWatch log group ARN for the worker"
  value       = aws_cloudwatch_log_group.worker.arn
}

output "celery_log_group_name" {
  description = "CloudWatch log group name for Celery"
  value       = aws_cloudwatch_log_group.celery.name
}

output "celery_log_group_arn" {
  description = "CloudWatch log group ARN for Celery"
  value       = aws_cloudwatch_log_group.celery.arn
}

output "ai_processing_log_group_name" {
  description = "CloudWatch log group name for AI processing"
  value       = aws_cloudwatch_log_group.ai_processing.name
}

output "ai_processing_log_group_arn" {
  description = "CloudWatch log group ARN for AI processing"
  value       = aws_cloudwatch_log_group.ai_processing.arn
}

output "interview_engine_log_group_name" {
  description = "CloudWatch log group name for the interview engine"
  value       = aws_cloudwatch_log_group.interview_engine.name
}

output "interview_engine_log_group_arn" {
  description = "CloudWatch log group ARN for the interview engine"
  value       = aws_cloudwatch_log_group.interview_engine.arn
}

output "application_log_group_name" {
  description = "CloudWatch log group name for the application"
  value       = aws_cloudwatch_log_group.application.name
}

output "application_log_group_arn" {
  description = "CloudWatch log group ARN for the application"
  value       = aws_cloudwatch_log_group.application.arn
}

output "nginx_log_group_name" {
  description = "CloudWatch log group name for Nginx"
  value       = aws_cloudwatch_log_group.nginx.name
}

output "nginx_log_group_arn" {
  description = "CloudWatch log group ARN for Nginx"
  value       = aws_cloudwatch_log_group.nginx.arn
}

output "database_log_group_name" {
  description = "CloudWatch log group name for database logs"
  value       = aws_cloudwatch_log_group.database.name
}

output "database_log_group_arn" {
  description = "CloudWatch log group ARN for database logs"
  value       = aws_cloudwatch_log_group.database.arn
}

output "audit_log_group_name" {
  description = "CloudWatch log group name for audit and security logs"
  value       = aws_cloudwatch_log_group.audit.name
}

output "audit_log_group_arn" {
  description = "CloudWatch log group ARN for audit and security logs"
  value       = aws_cloudwatch_log_group.audit.arn
}

output "errors_log_group_name" {
  description = "CloudWatch log group name for centralized errors"
  value       = aws_cloudwatch_log_group.errors.name
}

output "errors_log_group_arn" {
  description = "CloudWatch log group ARN for centralized errors"
  value       = aws_cloudwatch_log_group.errors.arn
}

# ------------------------------------------------------------
# All Log Groups
# ------------------------------------------------------------

output "log_groups" {
  description = "All CloudWatch log group names"
  value = {
    backend          = aws_cloudwatch_log_group.backend.name
    frontend         = aws_cloudwatch_log_group.frontend.name
    worker           = aws_cloudwatch_log_group.worker.name
    celery           = aws_cloudwatch_log_group.celery.name
    ai_processing    = aws_cloudwatch_log_group.ai_processing.name
    interview_engine = aws_cloudwatch_log_group.interview_engine.name
    application      = aws_cloudwatch_log_group.application.name
    nginx             = aws_cloudwatch_log_group.nginx.name
    database          = aws_cloudwatch_log_group.database.name
    audit             = aws_cloudwatch_log_group.audit.name
    errors            = aws_cloudwatch_log_group.errors.name
  }
}

# ------------------------------------------------------------
# Metric Namespaces
# ------------------------------------------------------------

output "application_metric_namespace" {
  description = "CloudWatch namespace for application metrics"
  value       = local.metric_namespace
}

output "ai_metric_namespace" {
  description = "CloudWatch namespace for AI metrics"
  value       = local.ai_metric_namespace
}

output "interview_metric_namespace" {
  description = "CloudWatch namespace for interview metrics"
  value       = local.interview_metric_namespace
}

output "celery_metric_namespace" {
  description = "CloudWatch namespace for Celery metrics"
  value       = local.celery_metric_namespace
}

output "database_metric_namespace" {
  description = "CloudWatch namespace for database metrics"
  value       = local.database_metric_namespace
}

output "security_metric_namespace" {
  description = "CloudWatch namespace for security metrics"
  value       = local.security_metric_namespace
}

# ------------------------------------------------------------
# Metric Filter Outputs
# ------------------------------------------------------------

output "metric_filters" {
  description = "CloudWatch metric filter names"

  value = {
    backend_errors            = aws_cloudwatch_log_metric_filter.backend_errors.name
    application_errors       = aws_cloudwatch_log_metric_filter.application_errors.name
    ai_processing_errors     = aws_cloudwatch_log_metric_filter.ai_processing_errors.name
    interview_errors         = aws_cloudwatch_log_metric_filter.interview_errors.name
    authentication_failures = aws_cloudwatch_log_metric_filter.authentication_failures.name
    resume_processing        = aws_cloudwatch_log_metric_filter.resume_processing.name
    interview_sessions       = aws_cloudwatch_log_metric_filter.interview_sessions.name
    api_requests             = aws_cloudwatch_log_metric_filter.api_requests.name
    http_5xx                 = aws_cloudwatch_log_metric_filter.http_5xx.name
    celery_failures          = aws_cloudwatch_log_metric_filter.celery_failures.name
    celery_completed         = aws_cloudwatch_log_metric_filter.celery_completed.name
    database_errors          = aws_cloudwatch_log_metric_filter.database_errors.name
    security_events          = aws_cloudwatch_log_metric_filter.security_events.name
    resume_uploads           = aws_cloudwatch_log_metric_filter.resume_uploads.name
    candidate_ranking        = aws_cloudwatch_log_metric_filter.candidate_ranking.name
    resume_matching          = aws_cloudwatch_log_metric_filter.resume_matching.name
    ats_scoring              = aws_cloudwatch_log_metric_filter.ats_scoring.name
  }
}

# ------------------------------------------------------------
# Retention
# ------------------------------------------------------------

output "log_retention_days" {
  description = "CloudWatch log retention period"
  value       = var.log_retention_days
}