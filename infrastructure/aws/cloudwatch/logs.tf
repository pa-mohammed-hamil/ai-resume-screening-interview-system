# ============================================================
# AWS CloudWatch Logs
# AI Resume Screening & Interview System
# ============================================================

# ------------------------------------------------------------
# Local Configuration
# ------------------------------------------------------------

locals {
  log_retention_days = var.log_retention_days

  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# ------------------------------------------------------------
# ECS Backend Log Group
# ------------------------------------------------------------

resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/${var.project_name}/backend"
  retention_in_days = local.log_retention_days

  tags = merge(local.common_tags, {
    Service = "backend"
  })
}

# ------------------------------------------------------------
# ECS Frontend Log Group
# ------------------------------------------------------------

resource "aws_cloudwatch_log_group" "frontend" {
  name              = "/ecs/${var.project_name}/frontend"
  retention_in_days = local.log_retention_days

  tags = merge(local.common_tags, {
    Service = "frontend"
  })
}

# ------------------------------------------------------------
# ECS Worker Log Group
# ------------------------------------------------------------

resource "aws_cloudwatch_log_group" "worker" {
  name              = "/ecs/${var.project_name}/worker"
  retention_in_days = local.log_retention_days

  tags = merge(local.common_tags, {
    Service = "worker"
  })
}

# ------------------------------------------------------------
# Celery Log Group
# ------------------------------------------------------------

resource "aws_cloudwatch_log_group" "celery" {
  name              = "/ecs/${var.project_name}/celery"
  retention_in_days = local.log_retention_days

  tags = merge(local.common_tags, {
    Service = "celery"
  })
}

# ------------------------------------------------------------
# AI Processing Log Group
# ------------------------------------------------------------

resource "aws_cloudwatch_log_group" "ai_processing" {
  name              = "/${var.project_name}/ai-processing"
  retention_in_days = local.log_retention_days

  tags = merge(local.common_tags, {
    Service = "ai-processing"
  })
}

# ------------------------------------------------------------
# Interview Engine Log Group
# ------------------------------------------------------------

resource "aws_cloudwatch_log_group" "interview_engine" {
  name              = "/${var.project_name}/interview-engine"
  retention_in_days = local.log_retention_days

  tags = merge(local.common_tags, {
    Service = "interview-engine"
  })
}

# ------------------------------------------------------------
# Application Log Group
# ------------------------------------------------------------

resource "aws_cloudwatch_log_group" "application" {
  name              = "/${var.project_name}/application"
  retention_in_days = local.log_retention_days

  tags = merge(local.common_tags, {
    Service = "application"
  })
}

# ------------------------------------------------------------
# Nginx Log Group
# ------------------------------------------------------------

resource "aws_cloudwatch_log_group" "nginx" {
  name              = "/${var.project_name}/nginx"
  retention_in_days = local.log_retention_days

  tags = merge(local.common_tags, {
    Service = "nginx"
  })
}

# ------------------------------------------------------------
# Database Log Group
# ------------------------------------------------------------

resource "aws_cloudwatch_log_group" "database" {
  name              = "/${var.project_name}/database"
  retention_in_days = local.log_retention_days

  tags = merge(local.common_tags, {
    Service = "database"
  })
}

# ------------------------------------------------------------
# Security / Audit Log Group
# ------------------------------------------------------------

resource "aws_cloudwatch_log_group" "audit" {
  name              = "/${var.project_name}/audit"
  retention_in_days = local.log_retention_days

  tags = merge(local.common_tags, {
    Service = "audit"
  })
}

# ------------------------------------------------------------
# Application Error Log Group
# ------------------------------------------------------------

resource "aws_cloudwatch_log_group" "errors" {
  name              = "/${var.project_name}/errors"
  retention_in_days = local.log_retention_days

  tags = merge(local.common_tags, {
    Service = "errors"
  })
}

# ------------------------------------------------------------
# CloudWatch Log Metric Filter - Backend Errors
# ------------------------------------------------------------

resource "aws_cloudwatch_log_metric_filter" "backend_errors" {
  name           = "${var.project_name}-backend-errors"
  log_group_name = aws_cloudwatch_log_group.backend.name
  pattern        = "[timestamp, request_id, level = ERROR, ...]"

  metric_transformation {
    name      = "BackendErrors"
    namespace = "${var.project_name}/Application"
    value     = "1"
  }
}

# ------------------------------------------------------------
# CloudWatch Log Metric Filter - Application Errors
# ------------------------------------------------------------

resource "aws_cloudwatch_log_metric_filter" "application_errors" {
  name           = "${var.project_name}-application-errors"
  log_group_name = aws_cloudwatch_log_group.application.name
  pattern        = "?ERROR ?CRITICAL ?Exception"

  metric_transformation {
    name      = "ApplicationErrors"
    namespace = "${var.project_name}/Application"
    value     = "1"
  }
}

# ------------------------------------------------------------
# CloudWatch Log Metric Filter - AI Processing Errors
# ------------------------------------------------------------

resource "aws_cloudwatch_log_metric_filter" "ai_processing_errors" {
  name           = "${var.project_name}-ai-processing-errors"
  log_group_name = aws_cloudwatch_log_group.ai_processing.name
  pattern        = "?ERROR ?Exception ?Failed"

  metric_transformation {
    name      = "AIProcessingErrors"
    namespace = "${var.project_name}/AI"
    value     = "1"
  }
}

# ------------------------------------------------------------
# CloudWatch Log Metric Filter - Interview Errors
# ------------------------------------------------------------

resource "aws_cloudwatch_log_metric_filter" "interview_errors" {
  name           = "${var.project_name}-interview-errors"
  log_group_name = aws_cloudwatch_log_group.interview_engine.name
  pattern        = "?ERROR ?Exception ?Failed"

  metric_transformation {
    name      = "InterviewErrors"
    namespace = "${var.project_name}/Interview"
    value     = "1"
  }
}

# ------------------------------------------------------------
# CloudWatch Log Metric Filter - Authentication Failures
# ------------------------------------------------------------

resource "aws_cloudwatch_log_metric_filter" "authentication_failures" {
  name           = "${var.project_name}-authentication-failures"
  log_group_name = aws_cloudwatch_log_group.audit.name
  pattern        = "?authentication_failed ?login_failed ?invalid_token"

  metric_transformation {
    name      = "AuthenticationFailures"
    namespace = "${var.project_name}/Security"
    value     = "1"
  }
}

# ------------------------------------------------------------
# CloudWatch Log Metric Filter - Resume Processing
# ------------------------------------------------------------

resource "aws_cloudwatch_log_metric_filter" "resume_processing" {
  name           = "${var.project_name}-resume-processing"
  log_group_name = aws_cloudwatch_log_group.ai_processing.name
  pattern        = "?resume_processed ?resume_analysis_completed"

  metric_transformation {
    name      = "ResumeProcessingCount"
    namespace = "${var.project_name}/AI"
    value     = "1"
  }
}

# ------------------------------------------------------------
# CloudWatch Log Metric Filter - Interview Sessions
# ------------------------------------------------------------

resource "aws_cloudwatch_log_metric_filter" "interview_sessions" {
  name           = "${var.project_name}-interview-sessions"
  log_group_name = aws_cloudwatch_log_group.interview_engine.name
  pattern        = "?interview_started ?interview_completed"

  metric_transformation {
    name      = "InterviewSessions"
    namespace = "${var.project_name}/Interview"
    value     = "1"
  }
}

# ------------------------------------------------------------
# CloudWatch Log Metric Filter - API Requests
# ------------------------------------------------------------

resource "aws_cloudwatch_log_metric_filter" "api_requests" {
  name           = "${var.project_name}-api-requests"
  log_group_name = aws_cloudwatch_log_group.backend.name
  pattern        = "?GET ?POST ?PUT ?DELETE"

  metric_transformation {
    name      = "APIRequests"
    namespace = "${var.project_name}/Application"
    value     = "1"
  }
}

# ------------------------------------------------------------
# CloudWatch Log Metric Filter - HTTP 5XX
# ------------------------------------------------------------

resource "aws_cloudwatch_log_metric_filter" "http_5xx" {
  name           = "${var.project_name}-http-5xx"
  log_group_name = aws_cloudwatch_log_group.backend.name
  pattern        = "?500 ?502 ?503 ?504"

  metric_transformation {
    name      = "HTTP5XXErrors"
    namespace = "${var.project_name}/Application"
    value     = "1"
  }
}

# ------------------------------------------------------------
# CloudWatch Log Metric Filter - Celery Task Failures
# ------------------------------------------------------------

resource "aws_cloudwatch_log_metric_filter" "celery_failures" {
  name           = "${var.project_name}-celery-task-failures"
  log_group_name = aws_cloudwatch_log_group.celery.name
  pattern        = "?FAILURE ?failed ?Exception"

  metric_transformation {
    name      = "CeleryTaskFailures"
    namespace = "${var.project_name}/Celery"
    value     = "1"
  }
}

# ------------------------------------------------------------
# CloudWatch Log Metric Filter - Celery Task Completed
# ------------------------------------------------------------

resource "aws_cloudwatch_log_metric_filter" "celery_completed" {
  name           = "${var.project_name}-celery-task-completed"
  log_group_name = aws_cloudwatch_log_group.celery.name
  pattern        = "?SUCCESS ?completed"

  metric_transformation {
    name      = "CeleryTaskCompleted"
    namespace = "${var.project_name}/Celery"
    value     = "1"
  }
}

# ------------------------------------------------------------
# CloudWatch Log Metric Filter - Database Errors
# ------------------------------------------------------------

resource "aws_cloudwatch_log_metric_filter" "database_errors" {
  name           = "${var.project_name}-database-errors"
  log_group_name = aws_cloudwatch_log_group.database.name
  pattern        = "?ERROR ?FATAL ?deadlock"

  metric_transformation {
    name      = "DatabaseErrors"
    namespace = "${var.project_name}/Database"
    value     = "1"
  }
}

# ------------------------------------------------------------
# CloudWatch Log Metric Filter - Security Events
# ------------------------------------------------------------

resource "aws_cloudwatch_log_metric_filter" "security_events" {
  name           = "${var.project_name}-security-events"
  log_group_name = aws_cloudwatch_log_group.audit.name
  pattern        = "?unauthorized ?forbidden ?suspicious"

  metric_transformation {
    name      = "SecurityEvents"
    namespace = "${var.project_name}/Security"
    value     = "1"
  }
}

# ------------------------------------------------------------
# CloudWatch Log Metric Filter - Resume Uploads
# ------------------------------------------------------------

resource "aws_cloudwatch_log_metric_filter" "resume_uploads" {
  name           = "${var.project_name}-resume-uploads"
  log_group_name = aws_cloudwatch_log_group.application.name
  pattern        = "?resume_uploaded ?file_uploaded"

  metric_transformation {
    name      = "ResumeUploads"
    namespace = "${var.project_name}/Application"
    value     = "1"
  }
}

# ------------------------------------------------------------
# CloudWatch Log Metric Filter - Candidate Ranking
# ------------------------------------------------------------

resource "aws_cloudwatch_log_metric_filter" "candidate_ranking" {
  name           = "${var.project_name}-candidate-ranking"
  log_group_name = aws_cloudwatch_log_group.ai_processing.name
  pattern        = "?candidate_ranked ?ranking_completed"

  metric_transformation {
    name      = "CandidateRankingCount"
    namespace = "${var.project_name}/AI"
    value     = "1"
  }
}

# ------------------------------------------------------------
# CloudWatch Log Metric Filter - Resume Matching
# ------------------------------------------------------------

resource "aws_cloudwatch_log_metric_filter" "resume_matching" {
  name           = "${var.project_name}-resume-matching"
  log_group_name = aws_cloudwatch_log_group.ai_processing.name
  pattern        = "?resume_job_match ?matching_completed"

  metric_transformation {
    name      = "ResumeMatchingCount"
    namespace = "${var.project_name}/AI"
    value     = "1"
  }
}

# ------------------------------------------------------------
# CloudWatch Log Metric Filter - ATS Scoring
# ------------------------------------------------------------

resource "aws_cloudwatch_log_metric_filter" "ats_scoring" {
  name           = "${var.project_name}-ats-scoring"
  log_group_name = aws_cloudwatch_log_group.ai_processing.name
  pattern        = "?ats_score_generated ?ats_scoring_completed"

  metric_transformation {
    name      = "ATSScoringCount"
    namespace = "${var.project_name}/AI"
    value     = "1"
  }
}