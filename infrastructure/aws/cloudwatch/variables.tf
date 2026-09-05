# ============================================================
# CloudWatch Variables
# AI Resume Screening & Interview System
# ============================================================

# ------------------------------------------------------------
# Project Configuration
# ------------------------------------------------------------

variable "project_name" {
  description = "Name of the AI Resume Screening & Interview System"
  type        = string
  default     = "ai-resume-system"

  validation {
    condition     = length(trimspace(var.project_name)) > 0
    error_message = "project_name must not be empty."
  }
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"

  validation {
    condition = contains(
      ["development", "staging", "production"],
      var.environment
    )
    error_message = "environment must be development, staging, or production."
  }
}

variable "aws_region" {
  description = "AWS region used by the CloudWatch resources"
  type        = string
  default     = "ap-south-1"
}

# ------------------------------------------------------------
# Log Configuration
# ------------------------------------------------------------

variable "log_retention_days" {
  description = "Number of days CloudWatch Logs are retained"
  type        = number
  default     = 30

  validation {
    condition = contains(
      [
        1,
        3,
        5,
        7,
        14,
        30,
        60,
        90,
        120,
        150,
        180,
        365,
        400,
        545,
        731,
        1827,
        3653
      ],
      var.log_retention_days
    )

    error_message = "log_retention_days must be a valid CloudWatch Logs retention value."
  }
}

# ------------------------------------------------------------
# Monitoring Configuration
# ------------------------------------------------------------

variable "enable_alarms" {
  description = "Enable CloudWatch alarms"
  type        = bool
  default     = true
}

variable "enable_dashboard" {
  description = "Enable the CloudWatch monitoring dashboard"
  type        = bool
  default     = true
}

variable "enable_metric_filters" {
  description = "Enable CloudWatch log metric filters"
  type        = bool
  default     = true
}

# ------------------------------------------------------------
# Alarm Configuration
# ------------------------------------------------------------

variable "alarm_evaluation_periods" {
  description = "Number of evaluation periods used by CloudWatch alarms"
  type        = number
  default     = 2

  validation {
    condition     = var.alarm_evaluation_periods >= 1
    error_message = "alarm_evaluation_periods must be at least 1."
  }
}

variable "alarm_period_seconds" {
  description = "CloudWatch alarm evaluation period in seconds"
  type        = number
  default     = 300

  validation {
    condition = contains(
      [10, 30, 60, 120, 180, 300, 600, 900, 1800, 3600],
      var.alarm_period_seconds
    )
    error_message = "alarm_period_seconds must be a supported CloudWatch period."
  }
}

variable "error_threshold" {
  description = "Number of application errors before triggering an alarm"
  type        = number
  default     = 10

  validation {
    condition     = var.error_threshold >= 1
    error_message = "error_threshold must be at least 1."
  }
}

variable "http_5xx_threshold" {
  description = "Number of HTTP 5XX errors before triggering an alarm"
  type        = number
  default     = 5

  validation {
    condition     = var.http_5xx_threshold >= 1
    error_message = "http_5xx_threshold must be at least 1."
  }
}

variable "celery_failure_threshold" {
  description = "Number of Celery task failures before triggering an alarm"
  type        = number
  default     = 5

  validation {
    condition     = var.celery_failure_threshold >= 1
    error_message = "celery_failure_threshold must be at least 1."
  }
}

variable "ai_error_threshold" {
  description = "Number of AI processing errors before triggering an alarm"
  type        = number
  default     = 5

  validation {
    condition     = var.ai_error_threshold >= 1
    error_message = "ai_error_threshold must be at least 1."
  }
}

variable "interview_error_threshold" {
  description = "Number of interview errors before triggering an alarm"
  type        = number
  default     = 5

  validation {
    condition     = var.interview_error_threshold >= 1
    error_message = "interview_error_threshold must be at least 1."
  }
}

variable "authentication_failure_threshold" {
  description = "Number of authentication failures before triggering an alarm"
  type        = number
  default     = 10

  validation {
    condition     = var.authentication_failure_threshold >= 1
    error_message = "authentication_failure_threshold must be at least 1."
  }
}

# ------------------------------------------------------------
# CPU / Memory Monitoring
# ------------------------------------------------------------

variable "backend_cpu_threshold" {
  description = "Backend ECS CPU utilization alarm threshold"
  type        = number
  default     = 80

  validation {
    condition     = var.backend_cpu_threshold > 0 && var.backend_cpu_threshold <= 100
    error_message = "backend_cpu_threshold must be between 1 and 100."
  }
}

variable "backend_memory_threshold" {
  description = "Backend ECS memory utilization alarm threshold"
  type        = number
  default     = 80

  validation {
    condition     = var.backend_memory_threshold > 0 && var.backend_memory_threshold <= 100
    error_message = "backend_memory_threshold must be between 1 and 100."
  }
}

variable "worker_cpu_threshold" {
  description = "Worker ECS CPU utilization alarm threshold"
  type        = number
  default     = 80

  validation {
    condition     = var.worker_cpu_threshold > 0 && var.worker_cpu_threshold <= 100
    error_message = "worker_cpu_threshold must be between 1 and 100."
  }
}

variable "worker_memory_threshold" {
  description = "Worker ECS memory utilization alarm threshold"
  type        = number
  default     = 80

  validation {
    condition     = var.worker_memory_threshold > 0 && var.worker_memory_threshold <= 100
    error_message = "worker_memory_threshold must be between 1 and 100."
  }
}

# ------------------------------------------------------------
# Database Monitoring
# ------------------------------------------------------------

variable "database_cpu_threshold" {
  description = "RDS CPU utilization alarm threshold"
  type        = number
  default     = 80

  validation {
    condition     = var.database_cpu_threshold > 0 && var.database_cpu_threshold <= 100
    error_message = "database_cpu_threshold must be between 1 and 100."
  }
}

variable "database_connection_threshold" {
  description = "Maximum number of database connections before alarming"
  type        = number
  default     = 80

  validation {
    condition     = var.database_connection_threshold >= 1
    error_message = "database_connection_threshold must be at least 1."
  }
}

variable "database_free_storage_threshold" {
  description = "Minimum free database storage in bytes"
  type        = number
  default     = 5368709120

  validation {
    condition     = var.database_free_storage_threshold > 0
    error_message = "database_free_storage_threshold must be greater than zero."
  }
}

# ------------------------------------------------------------
# SNS Notifications
# ------------------------------------------------------------

variable "enable_sns_notifications" {
  description = "Enable SNS notifications for CloudWatch alarms"
  type        = bool
  default     = false
}

variable "sns_topic_arn" {
  description = "SNS topic ARN used for CloudWatch alarm notifications"
  type        = string
  default     = ""
}

# ------------------------------------------------------------
# Dashboard Configuration
# ------------------------------------------------------------

variable "dashboard_name" {
  description = "Name of the CloudWatch dashboard"
  type        = string
  default     = "ai-resume-system-monitoring"
}

variable "dashboard_period_seconds" {
  description = "Default monitoring period used by dashboard widgets"
  type        = number
  default     = 300

  validation {
    condition = contains(
      [60, 300, 600, 900, 1800, 3600],
      var.dashboard_period_seconds
    )
    error_message = "dashboard_period_seconds must be a supported CloudWatch period."
  }
}

# ------------------------------------------------------------
# Tags
# ------------------------------------------------------------

variable "tags" {
  description = "Additional tags applied to CloudWatch resources"
  type        = map(string)
  default     = {}
}