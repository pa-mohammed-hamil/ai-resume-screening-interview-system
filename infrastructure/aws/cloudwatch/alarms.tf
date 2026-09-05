# ============================================================
# CloudWatch Alarms
# AI Resume Screening & Interview System
# ============================================================

# ------------------------------------------------------------
# SNS Topic for Alarm Notifications
# ------------------------------------------------------------

resource "aws_sns_topic" "alerts" {
  name = "${var.project_name}-alerts"

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_sns_topic_subscription" "email" {
  count = var.alert_email != "" ? 1 : 0

  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# ------------------------------------------------------------
# ECS CPU Utilization
# ------------------------------------------------------------

resource "aws_cloudwatch_metric_alarm" "ecs_cpu_high" {
  alarm_name          = "${var.project_name}-${var.environment}-ecs-cpu-high"
  alarm_description   = "ECS CPU utilization is above the configured threshold."
  comparison_operator = "GreaterThanThreshold"

  evaluation_periods = 3
  period              = 60
  threshold           = var.ecs_cpu_threshold

  namespace   = "AWS/ECS"
  metric_name = "CPUUtilization"
  statistic   = "Average"

  dimensions = {
    ClusterName = var.ecs_cluster_name
    ServiceName = var.ecs_service_name
  }

  treat_missing_data = "notBreaching"

  alarm_actions = [
    aws_sns_topic.alerts.arn
  ]

  ok_actions = [
    aws_sns_topic.alerts.arn
  ]

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Service     = "ecs"
    ManagedBy   = "Terraform"
  }
}

# ------------------------------------------------------------
# ECS Memory Utilization
# ------------------------------------------------------------

resource "aws_cloudwatch_metric_alarm" "ecs_memory_high" {
  alarm_name          = "${var.project_name}-${var.environment}-ecs-memory-high"
  alarm_description   = "ECS memory utilization is above the configured threshold."
  comparison_operator = "GreaterThanThreshold"

  evaluation_periods = 3
  period              = 60
  threshold           = var.ecs_memory_threshold

  namespace   = "AWS/ECS"
  metric_name = "MemoryUtilization"
  statistic   = "Average"

  dimensions = {
    ClusterName = var.ecs_cluster_name
    ServiceName = var.ecs_service_name
  }

  treat_missing_data = "notBreaching"

  alarm_actions = [
    aws_sns_topic.alerts.arn
  ]

  ok_actions = [
    aws_sns_topic.alerts.arn
  ]

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Service     = "ecs"
    ManagedBy   = "Terraform"
  }
}

# ------------------------------------------------------------
# ECS Running Task Count
# ------------------------------------------------------------

resource "aws_cloudwatch_metric_alarm" "ecs_running_tasks_low" {
  alarm_name          = "${var.project_name}-${var.environment}-ecs-running-tasks-low"
  alarm_description   = "ECS service has fewer running tasks than expected."
  comparison_operator = "LessThanThreshold"

  evaluation_periods = 2
  period              = 60
  threshold           = var.minimum_running_tasks

  namespace   = "ECS/ContainerInsights"
  metric_name = "RunningTaskCount"
  statistic   = "Minimum"

  dimensions = {
    ClusterName = var.ecs_cluster_name
    ServiceName = var.ecs_service_name
  }

  treat_missing_data = "breaching"

  alarm_actions = [
    aws_sns_topic.alerts.arn
  ]

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Service     = "ecs"
    ManagedBy   = "Terraform"
  }
}

# ------------------------------------------------------------
# ALB HTTP 5XX Errors
# ------------------------------------------------------------

resource "aws_cloudwatch_metric_alarm" "alb_5xx_high" {
  alarm_name          = "${var.project_name}-${var.environment}-alb-5xx-high"
  alarm_description   = "Application Load Balancer is returning a high number of HTTP 5XX errors."
  comparison_operator = "GreaterThanThreshold"

  evaluation_periods = 3
  period              = 60
  threshold           = var.alb_5xx_threshold

  namespace   = "AWS/ApplicationELB"
  metric_name = "HTTPCode_Target_5XX_Count"
  statistic   = "Sum"

  dimensions = {
    LoadBalancer = var.alb_arn_suffix
  }

  treat_missing_data = "notBreaching"

  alarm_actions = [
    aws_sns_topic.alerts.arn
  ]

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Service     = "alb"
    ManagedBy   = "Terraform"
  }
}

# ------------------------------------------------------------
# ALB Target Response Time
# ------------------------------------------------------------

resource "aws_cloudwatch_metric_alarm" "alb_response_time_high" {
  alarm_name          = "${var.project_name}-${var.environment}-alb-response-time-high"
  alarm_description   = "Application Load Balancer target response time is too high."
  comparison_operator = "GreaterThanThreshold"

  evaluation_periods = 3
  period              = 60
  threshold           = var.alb_response_time_threshold

  namespace   = "AWS/ApplicationELB"
  metric_name = "TargetResponseTime"
  statistic   = "Average"

  dimensions = {
    LoadBalancer = var.alb_arn_suffix
  }

  treat_missing_data = "notBreaching"

  alarm_actions = [
    aws_sns_topic.alerts.arn
  ]

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Service     = "alb"
    ManagedBy   = "Terraform"
  }
}

# ------------------------------------------------------------
# RDS CPU Utilization
# ------------------------------------------------------------

resource "aws_cloudwatch_metric_alarm" "rds_cpu_high" {
  alarm_name          = "${var.project_name}-${var.environment}-rds-cpu-high"
  alarm_description   = "RDS CPU utilization is above the configured threshold."
  comparison_operator = "GreaterThanThreshold"

  evaluation_periods = 3
  period              = 60
  threshold           = var.rds_cpu_threshold

  namespace   = "AWS/RDS"
  metric_name = "CPUUtilization"
  statistic   = "Average"

  dimensions = {
    DBInstanceIdentifier = var.rds_instance_identifier
  }

  treat_missing_data = "notBreaching"

  alarm_actions = [
    aws_sns_topic.alerts.arn
  ]

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Service     = "rds"
    ManagedBy   = "Terraform"
  }
}

# ------------------------------------------------------------
# RDS Free Storage Space
# ------------------------------------------------------------

resource "aws_cloudwatch_metric_alarm" "rds_storage_low" {
  alarm_name          = "${var.project_name}-${var.environment}-rds-storage-low"
  alarm_description   = "RDS free storage space is below the configured threshold."
  comparison_operator = "LessThanThreshold"

  evaluation_periods = 2
  period              = 300
  threshold           = var.rds_free_storage_threshold

  namespace   = "AWS/RDS"
  metric_name = "FreeStorageSpace"
  statistic   = "Minimum"

  dimensions = {
    DBInstanceIdentifier = var.rds_instance_identifier
  }

  treat_missing_data = "breaching"

  alarm_actions = [
    aws_sns_topic.alerts.arn
  ]

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Service     = "rds"
    ManagedBy   = "Terraform"
  }
}

# ------------------------------------------------------------
# RDS Database Connections
# ------------------------------------------------------------

resource "aws_cloudwatch_metric_alarm" "rds_connections_high" {
  alarm_name          = "${var.project_name}-${var.environment}-rds-connections-high"
  alarm_description   = "RDS database connection count is too high."
  comparison_operator = "GreaterThanThreshold"

  evaluation_periods = 3
  period              = 60
  threshold           = var.rds_connection_threshold

  namespace   = "AWS/RDS"
  metric_name = "DatabaseConnections"
  statistic   = "Average"

  dimensions = {
    DBInstanceIdentifier = var.rds_instance_identifier
  }

  treat_missing_data = "notBreaching"

  alarm_actions = [
    aws_sns_topic.alerts.arn
  ]

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Service     = "rds"
    ManagedBy   = "Terraform"
  }
}

# ------------------------------------------------------------
# RDS Freeable Memory
# ------------------------------------------------------------

resource "aws_cloudwatch_metric_alarm" "rds_memory_low" {
  alarm_name          = "${var.project_name}-${var.environment}-rds-memory-low"
  alarm_description   = "RDS freeable memory is below the configured threshold."
  comparison_operator = "LessThanThreshold"

  evaluation_periods = 3
  period              = 60
  threshold           = var.rds_freeable_memory_threshold

  namespace   = "AWS/RDS"
  metric_name = "FreeableMemory"
  statistic   = "Minimum"

  dimensions = {
    DBInstanceIdentifier = var.rds_instance_identifier
  }

  treat_missing_data = "notBreaching"

  alarm_actions = [
    aws_sns_topic.alerts.arn
  ]

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Service     = "rds"
    ManagedBy   = "Terraform"
  }
}

# ------------------------------------------------------------
# SQS / Celery Queue - Approximate Messages Visible
# ------------------------------------------------------------

resource "aws_cloudwatch_metric_alarm" "celery_queue_high" {
  count = var.celery_queue_name != "" ? 1 : 0

  alarm_name          = "${var.project_name}-${var.environment}-celery-queue-high"
  alarm_description   = "Celery task queue contains too many pending messages."
  comparison_operator = "GreaterThanThreshold"

  evaluation_periods = 3
  period              = 60
  threshold           = var.celery_queue_threshold

  namespace   = "AWS/SQS"
  metric_name = "ApproximateNumberOfMessagesVisible"
  statistic   = "Average"

  dimensions = {
    QueueName = var.celery_queue_name
  }

  treat_missing_data = "notBreaching"

  alarm_actions = [
    aws_sns_topic.alerts.arn
  ]

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Service     = "celery"
    ManagedBy   = "Terraform"
  }
}

# ------------------------------------------------------------
# S3 4XX Errors
# ------------------------------------------------------------

resource "aws_cloudwatch_metric_alarm" "s3_4xx_high" {
  count = var.s3_bucket_name != "" ? 1 : 0

  alarm_name          = "${var.project_name}-${var.environment}-s3-4xx-high"
  alarm_description   = "S3 is returning a high number of 4XX errors."
  comparison_operator = "GreaterThanThreshold"

  evaluation_periods = 3
  period              = 300
  threshold           = var.s3_4xx_threshold

  namespace   = "AWS/S3"
  metric_name = "4xxErrors"
  statistic   = "Sum"

  dimensions = {
    BucketName = var.s3_bucket_name
    FilterId   = "EntireBucket"
  }

  treat_missing_data = "notBreaching"

  alarm_actions = [
    aws_sns_topic.alerts.arn
  ]

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Service     = "s3"
    ManagedBy   = "Terraform"
  }
}

# ------------------------------------------------------------
# S3 5XX Errors
# ------------------------------------------------------------

resource "aws_cloudwatch_metric_alarm" "s3_5xx_high" {
  count = var.s3_bucket_name != "" ? 1 : 0

  alarm_name          = "${var.project_name}-${var.environment}-s3-5xx-high"
  alarm_description   = "S3 is returning a high number of 5XX errors."
  comparison_operator = "GreaterThanThreshold"

  evaluation_periods = 2
  period              = 300
  threshold           = var.s3_5xx_threshold

  namespace   = "AWS/S3"
  metric_name = "5xxErrors"
  statistic   = "Sum"

  dimensions = {
    BucketName = var.s3_bucket_name
    FilterId   = "EntireBucket"
  }

  treat_missing_data = "notBreaching"

  alarm_actions = [
    aws_sns_topic.alerts.arn
  ]

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Service     = "s3"
    ManagedBy   = "Terraform"
  }
}

# ------------------------------------------------------------
# Lambda / AI Processing Errors
# ------------------------------------------------------------

resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  count = var.lambda_function_name != "" ? 1 : 0

  alarm_name          = "${var.project_name}-${var.environment}-ai-processing-errors"
  alarm_description   = "AI processing Lambda is reporting errors."
  comparison_operator = "GreaterThanThreshold"

  evaluation_periods = 3
  period              = 60
  threshold           = var.lambda_error_threshold

  namespace   = "AWS/Lambda"
  metric_name = "Errors"
  statistic   = "Sum"

  dimensions = {
    FunctionName = var.lambda_function_name
  }

  treat_missing_data = "notBreaching"

  alarm_actions = [
    aws_sns_topic.alerts.arn
  ]

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Service     = "ai-processing"
    ManagedBy   = "Terraform"
  }
}

# ------------------------------------------------------------
# Lambda Duration
# ------------------------------------------------------------

resource "aws_cloudwatch_metric_alarm" "lambda_duration_high" {
  count = var.lambda_function_name != "" ? 1 : 0

  alarm_name          = "${var.project_name}-${var.environment}-ai-processing-duration-high"
  alarm_description   = "AI processing Lambda execution duration is too high."
  comparison_operator = "GreaterThanThreshold"

  evaluation_periods = 3
  period              = 60
  threshold           = var.lambda_duration_threshold

  namespace   = "AWS/Lambda"
  metric_name = "Duration"
  statistic   = "Average"

  dimensions = {
    FunctionName = var.lambda_function_name
  }

  treat_missing_data = "notBreaching"

  alarm_actions = [
    aws_sns_topic.alerts.arn
  ]

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Service     = "ai-processing"
    ManagedBy   = "Terraform"
  }
}

# ------------------------------------------------------------
# Application Health Check
# ------------------------------------------------------------

resource "aws_cloudwatch_metric_alarm" "application_health" {
  count = var.application_health_metric_name != "" ? 1 : 0

  alarm_name          = "${var.project_name}-${var.environment}-application-health"
  alarm_description   = "Application health check is failing."
  comparison_operator = "LessThanThreshold"

  evaluation_periods = 2
  period              = 60
  threshold           = var.application_health_threshold

  namespace   = var.application_metric_namespace
  metric_name = var.application_health_metric_name
  statistic   = "Minimum"

  treat_missing_data = "breaching"

  alarm_actions = [
    aws_sns_topic.alerts.arn
  ]

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Service     = "application"
    ManagedBy   = "Terraform"
  }
}