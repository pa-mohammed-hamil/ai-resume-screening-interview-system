# ============================================================
# AI Resume Screening & Interview System
# AWS ECS Variables
# File: infrastructure/aws/ecs/variables.tf
# ============================================================


# ============================================================
# PROJECT
# ============================================================

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "ai-resume-screening"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1"
}

variable "log_level" {
  description = "Application log level"
  type        = string
  default     = "INFO"
}

variable "log_retention_days" {
  description = "CloudWatch log retention period in days"
  type        = number
  default     = 30
}


# ============================================================
# FRONTEND ECS
# ============================================================

variable "frontend_image" {
  description = "Docker image URI for the frontend"
  type        = string
}

variable "frontend_cpu" {
  description = "Frontend ECS task CPU units"
  type        = number
  default     = 256
}

variable "frontend_memory" {
  description = "Frontend ECS task memory in MB"
  type        = number
  default     = 512
}

variable "frontend_container_cpu" {
  description = "Frontend container CPU units"
  type        = number
  default     = 256
}

variable "frontend_container_memory" {
  description = "Frontend container memory in MB"
  type        = number
  default     = 512
}

variable "frontend_desired_count" {
  description = "Initial number of frontend ECS tasks"
  type        = number
  default     = 2
}

variable "frontend_min_capacity" {
  description = "Minimum frontend ECS tasks"
  type        = number
  default     = 2
}

variable "frontend_max_capacity" {
  description = "Maximum frontend ECS tasks"
  type        = number
  default     = 6
}

variable "api_base_url" {
  description = "Public API URL used by the frontend"
  type        = string
}


# ============================================================
# BACKEND ECS
# ============================================================

variable "backend_image" {
  description = "Docker image URI for the FastAPI backend"
  type        = string
}

variable "backend_cpu" {
  description = "Backend ECS task CPU units"
  type        = number
  default     = 1024
}

variable "backend_memory" {
  description = "Backend ECS task memory in MB"
  type        = number
  default     = 2048
}

variable "backend_container_cpu" {
  description = "Backend container CPU units"
  type        = number
  default     = 1024
}

variable "backend_container_memory" {
  description = "Backend container memory in MB"
  type        = number
  default     = 2048
}

variable "backend_desired_count" {
  description = "Initial number of backend ECS tasks"
  type        = number
  default     = 2
}

variable "backend_min_capacity" {
  description = "Minimum backend ECS tasks"
  type        = number
  default     = 2
}

variable "backend_max_capacity" {
  description = "Maximum backend ECS tasks"
  type        = number
  default     = 10
}


# ============================================================
# CELERY WORKER ECS
# ============================================================

variable "worker_image" {
  description = "Docker image URI for the Celery worker"
  type        = string
}

variable "worker_cpu" {
  description = "Celery worker ECS task CPU units"
  type        = number
  default     = 2048
}

variable "worker_memory" {
  description = "Celery worker ECS task memory in MB"
  type        = number
  default     = 4096
}

variable "worker_container_cpu" {
  description = "Celery worker container CPU units"
  type        = number
  default     = 2048
}

variable "worker_container_memory" {
  description = "Celery worker container memory in MB"
  type        = number
  default     = 4096
}

variable "worker_desired_count" {
  description = "Initial number of Celery worker ECS tasks"
  type        = number
  default     = 2
}

variable "worker_min_capacity" {
  description = "Minimum Celery worker ECS tasks"
  type        = number
  default     = 2
}

variable "worker_max_capacity" {
  description = "Maximum Celery worker ECS tasks"
  type        = number
  default     = 10
}


# ============================================================
# NETWORK
# ============================================================

variable "public_subnet_ids" {
  description = "Public subnet IDs used by the frontend ECS service"
  type        = list(string)
}

variable "private_subnet_ids" {
  description = "Private subnet IDs used by backend and worker ECS services"
  type        = list(string)
}

variable "frontend_security_group_id" {
  description = "Security group ID for the frontend ECS service"
  type        = string
}

variable "backend_security_group_id" {
  description = "Security group ID for the backend ECS service"
  type        = string
}

variable "worker_security_group_id" {
  description = "Security group ID for the Celery worker ECS service"
  type        = string
}


# ============================================================
# APPLICATION LOAD BALANCER
# ============================================================

variable "frontend_target_group_arn" {
  description = "ALB target group ARN for frontend"
  type        = string
}

variable "backend_target_group_arn" {
  description = "ALB target group ARN for backend"
  type        = string
}

variable "load_balancer_name" {
  description = "Application Load Balancer name"
  type        = string
  default     = ""
}


# ============================================================
# REDIS
# ============================================================

variable "redis_url" {
  description = "Redis connection URL used by FastAPI and Celery"
  type        = string
  sensitive   = true
}


# ============================================================
# S3 STORAGE
# ============================================================

variable "resume_bucket_name" {
  description = "S3 bucket for uploaded resumes"
  type        = string
}

variable "generated_resume_bucket_name" {
  description = "S3 bucket for generated/optimized resumes"
  type        = string
}

variable "interview_audio_bucket_name" {
  description = "S3 bucket for interview audio"
  type        = string
}

variable "interview_report_bucket_name" {
  description = "S3 bucket for generated interview reports"
  type        = string
}


# ============================================================
# IAM - SECRETS MANAGER
# ============================================================

variable "secret_arns" {
  description = "AWS Secrets Manager ARNs accessible by ECS"
  type        = list(string)
  default     = []
}


# ============================================================
# BACKEND SECRETS
# ============================================================

variable "backend_secrets" {
  description = "Secrets injected into the backend ECS container"
  type = list(object({
    name      = string
    valueFrom = string
  }))

  default   = []
  sensitive = true
}


# ============================================================
# WORKER SECRETS
# ============================================================

variable "worker_secrets" {
  description = "Secrets injected into the Celery worker ECS container"
  type = list(object({
    name      = string
    valueFrom = string
  }))

  default   = []
  sensitive = true
}


# ============================================================
# KMS
# ============================================================

variable "enable_kms_access" {
  description = "Enable KMS access for ECS tasks"
  type        = bool
  default     = false
}

variable "kms_key_arn" {
  description = "Customer-managed KMS key ARN"
  type        = string
  default     = "*"
}


# ============================================================
# AMAZON BEDROCK
# ============================================================

variable "enable_bedrock_access" {
  description = "Enable Amazon Bedrock access for AI/GenAI services"
  type        = bool
  default     = false
}

variable "bedrock_model_arns" {
  description = "Amazon Bedrock model ARNs allowed for ECS tasks"
  type        = list(string)
  default     = []
}


# ============================================================
# AMAZON TRANSCRIBE
# ============================================================

variable "enable_transcribe_access" {
  description = "Enable Amazon Transcribe access for voice interviews"
  type        = bool
  default     = false
}


# ============================================================
# AMAZON POLLY
# ============================================================

variable "enable_polly_access" {
  description = "Enable Amazon Polly access for text-to-speech"
  type        = bool
  default     = false
}


# ============================================================
# AMAZON SQS
# ============================================================

variable "enable_sqs_access" {
  description = "Enable Amazon SQS access"
  type        = bool
  default     = false
}

variable "sqs_queue_arns" {
  description = "SQS queue ARNs accessible by ECS tasks"
  type        = list(string)
  default     = []
}


# ============================================================
# CLOUDWATCH
# ============================================================

variable "enable_custom_cloudwatch_metrics" {
  description = "Allow ECS tasks to publish custom CloudWatch metrics"
  type        = bool
  default     = false
}


# ============================================================
# ECS EXECUTION ROLE
# ============================================================

variable "ecs_execution_role_arn" {
  description = "ECS task execution IAM role ARN"
  type        = string
  default     = ""
}


# ============================================================
# ECS TASK ROLE
# ============================================================

variable "ecs_task_role_arn" {
  description = "ECS task IAM role ARN"
  type        = string
  default     = ""
}


# ============================================================
# ECS
# ============================================================

variable "ecs_cluster_name" {
  description = "ECS cluster name"
  type        = string
  default     = ""
}


# ============================================================
# RDS
# ============================================================

variable "rds_instance_identifier" {
  description = "RDS PostgreSQL instance identifier"
  type        = string
  default     = ""
}