# ============================================================
# AI Resume Screening & Interview System
# AWS IAM Configuration
# File: infrastructure/aws/ecs/iam.tf
# ============================================================

# ============================================================
# ECS TASK EXECUTION ROLE
# ============================================================
#
# Used by ECS/Fargate to:
# - Pull container images from ECR
# - Write container logs to CloudWatch
# - Retrieve secrets/parameters when configured
#
# ============================================================

resource "aws_iam_role" "ecs_execution" {
  name = "${var.project_name}-${var.environment}-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-ecs-execution-role"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# ============================================================
# AWS MANAGED POLICY
# ECS TASK EXECUTION
# ============================================================

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role = aws_iam_role.ecs_execution.name

  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ============================================================
# ECS EXECUTION ROLE - SECRETS MANAGER
# ============================================================
#
# Allows ECS to retrieve application secrets.
#
# Restrict this policy further by supplying specific secret ARNs
# through var.secret_arns.
#
# ============================================================

resource "aws_iam_role_policy" "ecs_execution_secrets" {
  name = "${var.project_name}-${var.environment}-ecs-execution-secrets"
  role = aws_iam_role.ecs_execution.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "ReadApplicationSecrets"
        Effect = "Allow"

        Action = [
          "secretsmanager:GetSecretValue"
        ]

        Resource = var.secret_arns
      }
    ]
  })
}

# ============================================================
# ECS TASK ROLE
# ============================================================
#
# Used by the running application containers.
#
# This is different from the ECS execution role:
#
# Execution Role:
#   ECS infrastructure operations
#
# Task Role:
#   Application operations
#
# ============================================================

resource "aws_iam_role" "ecs_task" {
  name = "${var.project_name}-${var.environment}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-ecs-task-role"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# ============================================================
# APPLICATION S3 ACCESS
# ============================================================
#
# The backend/workers need access to:
#
# - Uploaded resumes
# - Generated resumes
# - Interview audio
# - Interview reports
# - Temporary files
#
# ============================================================

resource "aws_iam_role_policy" "ecs_task_s3" {
  name = "${var.project_name}-${var.environment}-s3-access"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [

      # --------------------------------------------------------
      # List buckets
      # --------------------------------------------------------

      {
        Sid    = "ListApplicationBuckets"
        Effect = "Allow"

        Action = [
          "s3:ListBucket"
        ]

        Resource = var.s3_bucket_arns
      },

      # --------------------------------------------------------
      # Read/write application files
      # --------------------------------------------------------

      {
        Sid    = "ApplicationObjectAccess"
        Effect = "Allow"

        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:GetObjectTagging",
          "s3:PutObjectTagging"
        ]

        Resource = var.s3_object_arns
      }
    ]
  })
}

# ============================================================
# ECS TASK ROLE - KMS ACCESS
# ============================================================
#
# Required only when S3/application data is encrypted using
# a customer-managed KMS key.
#
# ============================================================

resource "aws_iam_role_policy" "ecs_task_kms" {
  count = var.enable_kms_access ? 1 : 0

  name = "${var.project_name}-${var.environment}-kms-access"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "ApplicationKMSAccess"
        Effect = "Allow"

        Action = [
          "kms:Decrypt",
          "kms:Encrypt",
          "kms:GenerateDataKey",
          "kms:DescribeKey"
        ]

        Resource = var.kms_key_arn
      }
    ]
  })
}

# ============================================================
# ECS EXEC ROLE PERMISSIONS
# ============================================================
#
# Allows ECS Exec to communicate through AWS Systems Manager.
#
# Useful for production debugging:
#
# aws ecs execute-command ...
#
# ============================================================

resource "aws_iam_role_policy" "ecs_exec" {
  name = "${var.project_name}-${var.environment}-ecs-exec"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "ECSExecSSMMessages"
        Effect = "Allow"

        Action = [
          "ssmmessages:CreateControlChannel",
          "ssmmessages:CreateDataChannel",
          "ssmmessages:OpenControlChannel",
          "ssmmessages:OpenDataChannel"
        ]

        Resource = "*"
      }
    ]
  })
}

# ============================================================
# OPTIONAL BEDROCK ACCESS
# ============================================================
#
# Enable this if your GenAI layer uses Amazon Bedrock.
#
# Example:
#
# genai/
# ├── llm/
# ├── agents/
# └── copilot/
#
# ============================================================

resource "aws_iam_role_policy" "ecs_task_bedrock" {
  count = var.enable_bedrock_access ? 1 : 0

  name = "${var.project_name}-${var.environment}-bedrock-access"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "InvokeBedrockModels"
        Effect = "Allow"

        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]

        Resource = var.bedrock_model_arns
      }
    ]
  })
}

# ============================================================
# OPTIONAL TRANSCRIBE ACCESS
# ============================================================
#
# Enable this if voice interviews use Amazon Transcribe.
#
# ============================================================

resource "aws_iam_role_policy" "ecs_task_transcribe" {
  count = var.enable_transcribe_access ? 1 : 0

  name = "${var.project_name}-${var.environment}-transcribe-access"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "TranscribeAccess"
        Effect = "Allow"

        Action = [
          "transcribe:StartTranscriptionJob",
          "transcribe:GetTranscriptionJob",
          "transcribe:DeleteTranscriptionJob"
        ]

        Resource = "*"
      }
    ]
  })
}

# ============================================================
# OPTIONAL POLLY ACCESS
# ============================================================
#
# Enable this if text-to-speech is implemented using Amazon
# Polly.
#
# ============================================================

resource "aws_iam_role_policy" "ecs_task_polly" {
  count = var.enable_polly_access ? 1 : 0

  name = "${var.project_name}-${var.environment}-polly-access"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "PollyAccess"
        Effect = "Allow"

        Action = [
          "polly:SynthesizeSpeech"
        ]

        Resource = "*"
      }
    ]
  })
}

# ============================================================
# OPTIONAL SQS ACCESS
# ============================================================
#
# Can be used if the application later replaces/extends Celery
# queues with Amazon SQS.
#
# ============================================================

resource "aws_iam_role_policy" "ecs_task_sqs" {
  count = var.enable_sqs_access ? 1 : 0

  name = "${var.project_name}-${var.environment}-sqs-access"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "SQSApplicationAccess"
        Effect = "Allow"

        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes",
          "sqs:GetQueueUrl"
        ]

        Resource = var.sqs_queue_arns
      }
    ]
  })
}

# ============================================================
# ECS TASK ROLE - CLOUDWATCH METRICS
# ============================================================
#
# Allows the application to publish custom application metrics
# when required.
#
# ============================================================

resource "aws_iam_role_policy" "ecs_task_cloudwatch" {
  count = var.enable_custom_cloudwatch_metrics ? 1 : 0

  name = "${var.project_name}-${var.environment}-cloudwatch-metrics"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "PublishApplicationMetrics"
        Effect = "Allow"

        Action = [
          "cloudwatch:PutMetricData"
        ]

        Resource = "*"
      }
    ]
  })
}

# ============================================================
# IAM INSTANCE PROFILE
# ============================================================
#
# Not required for Fargate.
#
# Kept disabled intentionally because this project uses
# ECS Fargate instead of ECS EC2.
#
# ============================================================

# No aws_iam_instance_profile is required.