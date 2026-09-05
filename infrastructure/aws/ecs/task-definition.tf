# ============================================================
# AI Resume Screening & Interview System
# AWS ECS Task Definitions
# File: infrastructure/aws/ecs/task-definition.tf
# ============================================================

# ============================================================
# FRONTEND TASK DEFINITION
# ============================================================

resource "aws_ecs_task_definition" "frontend" {
  family                   = "${var.project_name}-${var.environment}-frontend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]

  cpu    = var.frontend_cpu
  memory = var.frontend_memory

  execution_role_arn = aws_iam_role.ecs_execution.arn
  task_role_arn      = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "frontend"
      image     = var.frontend_image
      essential = true

      cpu    = var.frontend_container_cpu
      memory = var.frontend_container_memory

      portMappings = [
        {
          name          = "frontend-http"
          containerPort = 80
          hostPort      = 80
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "ENVIRONMENT"
          value = var.environment
        },

        {
          name  = "API_BASE_URL"
          value = var.api_base_url
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"

        options = {
          awslogs-group         = aws_cloudwatch_log_group.frontend.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "frontend"
        }
      }

      healthCheck = {
        command = [
          "CMD-SHELL",
          "wget --no-verbose --tries=1 --spider http://localhost/ || exit 1"
        ]

        interval = 30
        timeout  = 5
        retries  = 3
        startPeriod = 20
      }

      readonlyRootFilesystem = false

      stopTimeout = 30
    }
  ])

  tags = {
    Name        = "${var.project_name}-frontend-task"
    Project     = var.project_name
    Environment = var.environment
    Service     = "frontend"
    ManagedBy   = "Terraform"
  }
}


# ============================================================
# BACKEND TASK DEFINITION
# ============================================================

resource "aws_ecs_task_definition" "backend" {
  family                   = "${var.project_name}-${var.environment}-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]

  cpu    = var.backend_cpu
  memory = var.backend_memory

  execution_role_arn = aws_iam_role.ecs_execution.arn
  task_role_arn      = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "backend"
      image     = var.backend_image
      essential = true

      cpu    = var.backend_container_cpu
      memory = var.backend_container_memory

      portMappings = [
        {
          name          = "backend-http"
          containerPort = 8000
          hostPort      = 8000
          protocol      = "tcp"
        }
      ]

      command = [
        "uvicorn",
        "app.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000"
      ]

      environment = [
        {
          name  = "ENVIRONMENT"
          value = var.environment
        },

        {
          name  = "AWS_REGION"
          value = var.aws_region
        },

        {
          name  = "PYTHONUNBUFFERED"
          value = "1"
        },

        {
          name  = "LOG_LEVEL"
          value = var.log_level
        },

        {
          name  = "S3_RESUME_BUCKET"
          value = var.resume_bucket_name
        },

        {
          name  = "S3_GENERATED_RESUME_BUCKET"
          value = var.generated_resume_bucket_name
        },

        {
          name  = "S3_INTERVIEW_AUDIO_BUCKET"
          value = var.interview_audio_bucket_name
        },

        {
          name  = "S3_INTERVIEW_REPORT_BUCKET"
          value = var.interview_report_bucket_name
        },

        {
          name  = "REDIS_URL"
          value = var.redis_url
        }
      ]

      secrets = var.backend_secrets

      logConfiguration = {
        logDriver = "awslogs"

        options = {
          awslogs-group         = aws_cloudwatch_log_group.backend.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "backend"
        }
      }

      healthCheck = {
        command = [
          "CMD-SHELL",
          "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=5)\" || exit 1"
        ]

        interval    = 30
        timeout     = 10
        retries     = 3
        startPeriod = 60
      }

      readonlyRootFilesystem = false

      stopTimeout = 60
    }
  ])

  tags = {
    Name        = "${var.project_name}-backend-task"
    Project     = var.project_name
    Environment = var.environment
    Service     = "backend"
    ManagedBy   = "Terraform"
  }
}


# ============================================================
# CELERY WORKER TASK DEFINITION
# ============================================================

resource "aws_ecs_task_definition" "worker" {
  family                   = "${var.project_name}-${var.environment}-worker"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]

  cpu    = var.worker_cpu
  memory = var.worker_memory

  execution_role_arn = aws_iam_role.ecs_execution.arn
  task_role_arn      = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "worker"
      image     = var.worker_image
      essential = true

      cpu    = var.worker_container_cpu
      memory = var.worker_container_memory

      command = [
        "celery",
        "-A",
        "app.workers.celery_app",
        "worker",
        "--loglevel=INFO",
        "--concurrency=2"
      ]

      environment = [
        {
          name  = "ENVIRONMENT"
          value = var.environment
        },

        {
          name  = "AWS_REGION"
          value = var.aws_region
        },

        {
          name  = "PYTHONUNBUFFERED"
          value = "1"
        },

        {
          name  = "LOG_LEVEL"
          value = var.log_level
        },

        {
          name  = "S3_RESUME_BUCKET"
          value = var.resume_bucket_name
        },

        {
          name  = "S3_GENERATED_RESUME_BUCKET"
          value = var.generated_resume_bucket_name
        },

        {
          name  = "S3_INTERVIEW_AUDIO_BUCKET"
          value = var.interview_audio_bucket_name
        },

        {
          name  = "S3_INTERVIEW_REPORT_BUCKET"
          value = var.interview_report_bucket_name
        },

        {
          name  = "REDIS_URL"
          value = var.redis_url
        }
      ]

      secrets = var.worker_secrets

      logConfiguration = {
        logDriver = "awslogs"

        options = {
          awslogs-group         = aws_cloudwatch_log_group.worker.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "worker"
        }
      }

      healthCheck = {
        command = [
          "CMD-SHELL",
          "celery -A app.workers.celery_app inspect ping -d celery@$$HOSTNAME || exit 1"
        ]

        interval    = 60
        timeout     = 20
        retries     = 3
        startPeriod = 90
      }

      readonlyRootFilesystem = false

      stopTimeout = 120
    }
  ])

  tags = {
    Name        = "${var.project_name}-worker-task"
    Project     = var.project_name
    Environment = var.environment
    Service     = "celery-worker"
    ManagedBy   = "Terraform"
  }
}