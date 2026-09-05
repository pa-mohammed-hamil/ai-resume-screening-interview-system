# infrastructure/aws/cloudwatch/dashboard.tf

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.project_name}-dashboard"

  dashboard_body = jsonencode({
    widgets = [

      # ============================================================
      # ECS BACKEND - CPU
      # ============================================================
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          title  = "Backend CPU Utilization"
          region = var.aws_region

          view   = "timeSeries"
          stacked = false

          period = 300
          stat   = "Average"

          yAxis = {
            left = {
              min = 0
              max = 100
            }
          }

          metrics = [
            [
              "AWS/ECS",
              "CPUUtilization",
              "ClusterName",
              var.ecs_cluster_name,
              "ServiceName",
              var.backend_service_name
            ]
          ]
        }
      },

      # ============================================================
      # ECS BACKEND - MEMORY
      # ============================================================
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6

        properties = {
          title  = "Backend Memory Utilization"
          region = var.aws_region

          view    = "timeSeries"
          stacked = false

          period = 300
          stat   = "Average"

          yAxis = {
            left = {
              min = 0
              max = 100
            }
          }

          metrics = [
            [
              "AWS/ECS",
              "MemoryUtilization",
              "ClusterName",
              var.ecs_cluster_name,
              "ServiceName",
              var.backend_service_name
            ]
          ]
        }
      },

      # ============================================================
      # ECS WORKER - CPU
      # ============================================================
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6

        properties = {
          title  = "Celery Worker CPU"
          region = var.aws_region

          view    = "timeSeries"
          stacked = false

          period = 300
          stat   = "Average"

          metrics = [
            [
              "AWS/ECS",
              "CPUUtilization",
              "ClusterName",
              var.ecs_cluster_name,
              "ServiceName",
              var.worker_service_name
            ]
          ]
        }
      },

      # ============================================================
      # ECS WORKER - MEMORY
      # ============================================================
      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 6

        properties = {
          title  = "Celery Worker Memory"
          region = var.aws_region

          view    = "timeSeries"
          stacked = false

          period = 300
          stat   = "Average"

          metrics = [
            [
              "AWS/ECS",
              "MemoryUtilization",
              "ClusterName",
              var.ecs_cluster_name,
              "ServiceName",
              var.worker_service_name
            ]
          ]
        }
      },

      # ============================================================
      # APPLICATION LOAD BALANCER - REQUEST COUNT
      # ============================================================
      {
        type   = "metric"
        x      = 0
        y      = 12
        width  = 12
        height = 6

        properties = {
          title  = "API Request Count"
          region = var.aws_region

          view    = "timeSeries"
          stacked = false

          period = 300
          stat   = "Sum"

          metrics = [
            [
              "AWS/ApplicationELB",
              "RequestCount",
              "LoadBalancer",
              var.load_balancer_name
            ]
          ]
        }
      },

      # ============================================================
      # ALB - RESPONSE TIME
      # ============================================================
      {
        type   = "metric"
        x      = 12
        y      = 12
        width  = 12
        height = 6

        properties = {
          title  = "API Response Time"
          region = var.aws_region

          view    = "timeSeries"
          stacked = false

          period = 300
          stat   = "Average"

          metrics = [
            [
              "AWS/ApplicationELB",
              "TargetResponseTime",
              "LoadBalancer",
              var.load_balancer_name
            ]
          ]
        }
      },

      # ============================================================
      # ALB - HTTP 5XX
      # ============================================================
      {
        type   = "metric"
        x      = 0
        y      = 18
        width  = 12
        height = 6

        properties = {
          title  = "HTTP 5XX Errors"
          region = var.aws_region

          view    = "timeSeries"
          stacked = false

          period = 300
          stat   = "Sum"

          metrics = [
            [
              "AWS/ApplicationELB",
              "HTTPCode_Target_5XX_Count",
              "LoadBalancer",
              var.load_balancer_name
            ]
          ]
        }
      },

      # ============================================================
      # ALB - HTTP 4XX
      # ============================================================
      {
        type   = "metric"
        x      = 12
        y      = 18
        width  = 12
        height = 6

        properties = {
          title  = "HTTP 4XX Errors"
          region = var.aws_region

          view    = "timeSeries"
          stacked = false

          period = 300
          stat   = "Sum"

          metrics = [
            [
              "AWS/ApplicationELB",
              "HTTPCode_Target_4XX_Count",
              "LoadBalancer",
              var.load_balancer_name
            ]
          ]
        }
      },

      # ============================================================
      # RDS CPU
      # ============================================================
      {
        type   = "metric"
        x      = 0
        y      = 24
        width  = 12
        height = 6

        properties = {
          title  = "PostgreSQL CPU Utilization"
          region = var.aws_region

          view    = "timeSeries"
          stacked = false

          period = 300
          stat   = "Average"

          metrics = [
            [
              "AWS/RDS",
              "CPUUtilization",
              "DBInstanceIdentifier",
              var.rds_instance_identifier
            ]
          ]
        }
      },

      # ============================================================
      # RDS CONNECTIONS
      # ============================================================
      {
        type   = "metric"
        x      = 12
        y      = 24
        width  = 12
        height = 6

        properties = {
          title  = "PostgreSQL Database Connections"
          region = var.aws_region

          view    = "timeSeries"
          stacked = false

          period = 300
          stat   = "Average"

          metrics = [
            [
              "AWS/RDS",
              "DatabaseConnections",
              "DBInstanceIdentifier",
              var.rds_instance_identifier
            ]
          ]
        }
      },

      # ============================================================
      # RDS FREE STORAGE
      # ============================================================
      {
        type   = "metric"
        x      = 0
        y      = 30
        width  = 12
        height = 6

        properties = {
          title  = "RDS Free Storage"
          region = var.aws_region

          view    = "timeSeries"
          stacked = false

          period = 300
          stat   = "Average"

          metrics = [
            [
              "AWS/RDS",
              "FreeStorageSpace",
              "DBInstanceIdentifier",
              var.rds_instance_identifier
            ]
          ]
        }
      },

      # ============================================================
      # ECS RUNNING TASKS
      # ============================================================
      {
        type   = "metric"
        x      = 12
        y      = 30
        width  = 12
        height = 6

        properties = {
          title  = "ECS Running Tasks"
          region = var.aws_region

          view    = "timeSeries"
          stacked = false

          period = 300
          stat   = "Average"

          metrics = [
            [
              "ECS/ContainerInsights",
              "RunningTaskCount",
              "ClusterName",
              var.ecs_cluster_name,
              "ServiceName",
              var.backend_service_name
            ],
            [
              "ECS/ContainerInsights",
              "RunningTaskCount",
              "ClusterName",
              var.ecs_cluster_name,
              "ServiceName",
              var.worker_service_name
            ]
          ]
        }
      },

      # ============================================================
      # CONTAINER INSIGHTS - NETWORK
      # ============================================================
      {
        type   = "metric"
        x      = 0
        y      = 36
        width  = 12
        height = 6

        properties = {
          title  = "Backend Network Traffic"
          region = var.aws_region

          view    = "timeSeries"
          stacked = false

          period = 300
          stat   = "Average"

          metrics = [
            [
              "ECS/ContainerInsights",
              "NetworkRxBytes",
              "ClusterName",
              var.ecs_cluster_name,
              "ServiceName",
              var.backend_service_name
            ],
            [
              "ECS/ContainerInsights",
              "NetworkTxBytes",
              "ClusterName",
              var.ecs_cluster_name,
              "ServiceName",
              var.backend_service_name
            ]
          ]
        }
      },

      # ============================================================
      # RDS READ / WRITE IOPS
      # ============================================================
      {
        type   = "metric"
        x      = 12
        y      = 36
        width  = 12
        height = 6

        properties = {
          title  = "RDS I/O Operations"
          region = var.aws_region

          view    = "timeSeries"
          stacked = false

          period = 300
          stat   = "Average"

          metrics = [
            [
              "AWS/RDS",
              "ReadIOPS",
              "DBInstanceIdentifier",
              var.rds_instance_identifier
            ],
            [
              "AWS/RDS",
              "WriteIOPS",
              "DBInstanceIdentifier",
              var.rds_instance_identifier
            ]
          ]
        }
      },

      # ============================================================
      # S3 STORAGE
      # ============================================================
      {
        type   = "metric"
        x      = 0
        y      = 42
        width  = 12
        height = 6

        properties = {
          title  = "S3 Storage Usage"
          region = var.aws_region

          view    = "timeSeries"
          stacked = false

          period = 86400
          stat   = "Average"

          metrics = [
            [
              "AWS/S3",
              "BucketSizeBytes",
              "BucketName",
              var.resume_bucket_name,
              "StorageType",
              "StandardStorage"
            ]
          ]
        }
      },

      # ============================================================
      # S3 OBJECT COUNT
      # ============================================================
      {
        type   = "metric"
        x      = 12
        y      = 42
        width  = 12
        height = 6

        properties = {
          title  = "Resume S3 Object Count"
          region = var.aws_region

          view    = "timeSeries"
          stacked = false

          period = 86400
          stat   = "Average"

          metrics = [
            [
              "AWS/S3",
              "NumberOfObjects",
              "BucketName",
              var.resume_bucket_name,
              "StorageType",
              "AllStorageTypes"
            ]
          ]
        }
      }
    ]
  })
}