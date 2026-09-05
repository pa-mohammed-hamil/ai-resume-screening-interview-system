# ============================================================
# AI Resume Screening & Interview System
# AWS ECS Cluster
# File: infrastructure/aws/ecs/cluster.tf
# ============================================================

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

# ============================================================
# ECS CLUSTER
# ============================================================

resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"

  # ----------------------------------------------------------
  # Enable CloudWatch Container Insights
  # ----------------------------------------------------------

  setting {
    name  = "containerInsights"
    value = "enhanced"
  }

  # ----------------------------------------------------------
  # ECS Cluster Configuration
  # ----------------------------------------------------------

  configuration {
    execute_command_configuration {
      logging = "OVERRIDE"

      log_configuration {
        cloud_watch_log_group_name = aws_cloudwatch_log_group.ecs_exec.name
      }
    }
  }

  tags = {
    Name        = "${var.project_name}-cluster"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# ============================================================
# CLOUDWATCH LOG GROUP
# ECS EXECUTION COMMAND LOGS
# ============================================================

resource "aws_cloudwatch_log_group" "ecs_exec" {
  name              = "/ecs/${var.project_name}/exec"
  retention_in_days = var.log_retention_days

  tags = {
    Name        = "${var.project_name}-ecs-exec-logs"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# ============================================================
# CLOUDWATCH LOG GROUP
# BACKEND APPLICATION
# ============================================================

resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/${var.project_name}/backend"
  retention_in_days = var.log_retention_days

  tags = {
    Name        = "${var.project_name}-backend-logs"
    Project     = var.project_name
    Environment = var.environment
    Service     = "backend"
    ManagedBy   = "Terraform"
  }
}

# ============================================================
# CLOUDWATCH LOG GROUP
# CELERY WORKER
# ============================================================

resource "aws_cloudwatch_log_group" "worker" {
  name              = "/ecs/${var.project_name}/worker"
  retention_in_days = var.log_retention_days

  tags = {
    Name        = "${var.project_name}-worker-logs"
    Project     = var.project_name
    Environment = var.environment
    Service     = "worker"
    ManagedBy   = "Terraform"
  }
}

# ============================================================
# CLOUDWATCH LOG GROUP
# FRONTEND / NGINX
# ============================================================

resource "aws_cloudwatch_log_group" "frontend" {
  name              = "/ecs/${var.project_name}/frontend"
  retention_in_days = var.log_retention_days

  tags = {
    Name        = "${var.project_name}-frontend-logs"
    Project     = var.project_name
    Environment = var.environment
    Service     = "frontend"
    ManagedBy   = "Terraform"
  }
}

# ============================================================
# CLOUDWATCH LOG GROUP
# RESUME PROCESSING
# ============================================================

resource "aws_cloudwatch_log_group" "resume_processing" {
  name              = "/ecs/${var.project_name}/resume-processing"
  retention_in_days = var.log_retention_days

  tags = {
    Name        = "${var.project_name}-resume-processing-logs"
    Project     = var.project_name
    Environment = var.environment
    Service     = "resume-processing"
    ManagedBy   = "Terraform"
  }
}

# ============================================================
# CLOUDWATCH LOG GROUP
# INTERVIEW PROCESSING
# ============================================================

resource "aws_cloudwatch_log_group" "interview_processing" {
  name              = "/ecs/${var.project_name}/interview-processing"
  retention_in_days = var.log_retention_days

  tags = {
    Name        = "${var.project_name}-interview-processing-logs"
    Project     = var.project_name
    Environment = var.environment
    Service     = "interview-processing"
    ManagedBy   = "Terraform"
  }
}

# ============================================================
# CLOUDWATCH LOG GROUP
# AI / GENAI PROCESSING
# ============================================================

resource "aws_cloudwatch_log_group" "ai_processing" {
  name              = "/ecs/${var.project_name}/ai-processing"
  retention_in_days = var.log_retention_days

  tags = {
    Name        = "${var.project_name}-ai-processing-logs"
    Project     = var.project_name
    Environment = var.environment
    Service     = "ai-processing"
    ManagedBy   = "Terraform"
  }
}

# ============================================================
# CLOUDWATCH LOG GROUP
# RAG PROCESSING
# ============================================================

resource "aws_cloudwatch_log_group" "rag_processing" {
  name              = "/ecs/${var.project_name}/rag-processing"
  retention_in_days = var.log_retention_days

  tags = {
    Name        = "${var.project_name}-rag-processing-logs"
    Project     = var.project_name
    Environment = var.environment
    Service     = "rag-processing"
    ManagedBy   = "Terraform"
  }
}

# ============================================================
# CLOUDWATCH LOG GROUP
# REPORT GENERATION
# ============================================================

resource "aws_cloudwatch_log_group" "report_processing" {
  name              = "/ecs/${var.project_name}/report-processing"
  retention_in_days = var.log_retention_days

  tags = {
    Name        = "${var.project_name}-report-processing-logs"
    Project     = var.project_name
    Environment = var.environment
    Service     = "report-processing"
    ManagedBy   = "Terraform"
  }
}

# ============================================================
# ECS CLUSTER CAPACITY PROVIDER
# ============================================================
#
# The application uses AWS Fargate, so there is no EC2
# capacity that needs to be manually managed.
#
# FARGATE:
#   General application workloads
#
# FARGATE_SPOT:
#   Optional lower-cost workloads such as background workers
#
# ============================================================

resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name = aws_ecs_cluster.main.name

  capacity_providers = [
    "FARGATE",
    "FARGATE_SPOT"
  ]

  default_capacity_provider_strategy {
    base              = 1
    weight            = 70
    capacity_provider = "FARGATE"
  }

  default_capacity_provider_strategy {
    weight            = 30
    capacity_provider = "FARGATE_SPOT"
  }
}

# ============================================================
# ECS CLUSTER TAGS
# ============================================================

resource "aws_ecs_cluster" "tags_placeholder" {
  count = 0

  name = "${var.project_name}-tags-placeholder"
}