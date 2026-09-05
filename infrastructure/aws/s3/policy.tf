# ============================================================
# AI Resume Screening & Interview System
# AWS S3 IAM Policy
# File: infrastructure/aws/s3/policy.tf
# ============================================================


# ============================================================
# S3 APPLICATION ACCESS POLICY
# ============================================================

resource "aws_iam_policy" "s3_application_access" {
  name        = "${var.project_name}-${var.environment}-s3-access"
  description = "Least-privilege S3 access for the AI Resume Screening and Interview System"

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [

      # --------------------------------------------------------
      # LIST BUCKETS
      # --------------------------------------------------------

      {
        Sid    = "ListApplicationBuckets"
        Effect = "Allow"

        Action = [
          "s3:ListBucket"
        ]

        Resource = [
          aws_s3_bucket.resumes.arn,
          aws_s3_bucket.generated_resumes.arn,
          aws_s3_bucket.interview_audio.arn,
          aws_s3_bucket.interview_reports.arn,
          aws_s3_bucket.temporary.arn
        ]
      },


      # --------------------------------------------------------
      # RESUME FILE ACCESS
      # --------------------------------------------------------

      {
        Sid    = "ResumeObjectAccess"
        Effect = "Allow"

        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:PutObject",
          "s3:AbortMultipartUpload"
        ]

        Resource = "${aws_s3_bucket.resumes.arn}/*"
      },


      # --------------------------------------------------------
      # GENERATED RESUME ACCESS
      # --------------------------------------------------------

      {
        Sid    = "GeneratedResumeObjectAccess"
        Effect = "Allow"

        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:AbortMultipartUpload"
        ]

        Resource = "${aws_s3_bucket.generated_resumes.arn}/*"
      },


      # --------------------------------------------------------
      # INTERVIEW AUDIO ACCESS
      # --------------------------------------------------------

      {
        Sid    = "InterviewAudioObjectAccess"
        Effect = "Allow"

        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:AbortMultipartUpload"
        ]

        Resource = "${aws_s3_bucket.interview_audio.arn}/*"
      },


      # --------------------------------------------------------
      # INTERVIEW REPORT ACCESS
      # --------------------------------------------------------

      {
        Sid    = "InterviewReportObjectAccess"
        Effect = "Allow"

        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:AbortMultipartUpload"
        ]

        Resource = "${aws_s3_bucket.interview_reports.arn}/*"
      },


      # --------------------------------------------------------
      # TEMPORARY FILE ACCESS
      # --------------------------------------------------------

      {
        Sid    = "TemporaryObjectAccess"
        Effect = "Allow"

        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:AbortMultipartUpload"
        ]

        Resource = "${aws_s3_bucket.temporary.arn}/*"
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-s3-access"
    Project     = var.project_name
    Environment = var.environment
    Service     = "s3"
    ManagedBy   = "Terraform"
  }
}


# ============================================================
# OPTIONAL KMS POLICY
# ============================================================

resource "aws_iam_policy" "s3_kms_access" {
  count = var.kms_key_arn != "" ? 1 : 0

  name        = "${var.project_name}-${var.environment}-s3-kms-access"
  description = "KMS permissions for encrypted S3 objects"

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "S3KMSAccess"
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

  tags = {
    Name        = "${var.project_name}-${var.environment}-s3-kms-access"
    Project     = var.project_name
    Environment = var.environment
    Service     = "s3"
    ManagedBy   = "Terraform"
  }
}