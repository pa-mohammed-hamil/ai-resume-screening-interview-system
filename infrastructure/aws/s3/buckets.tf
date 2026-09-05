# ============================================================
# AI Resume Screening & Interview System
# AWS S3 Buckets
# File: infrastructure/aws/s3/buckets.tf
# ============================================================


# ============================================================
# RESUME BUCKET
# ============================================================

resource "aws_s3_bucket" "resumes" {
  bucket = "${var.project_name}-${var.environment}-resumes-${var.bucket_suffix}"

  force_destroy = var.force_destroy

  tags = {
    Name        = "${var.project_name}-${var.environment}-resumes"
    Project     = var.project_name
    Environment = var.environment
    Service     = "resume-storage"
    ManagedBy   = "Terraform"
  }
}


# ============================================================
# GENERATED RESUME BUCKET
# ============================================================

resource "aws_s3_bucket" "generated_resumes" {
  bucket = "${var.project_name}-${var.environment}-generated-resumes-${var.bucket_suffix}"

  force_destroy = var.force_destroy

  tags = {
    Name        = "${var.project_name}-${var.environment}-generated-resumes"
    Project     = var.project_name
    Environment = var.environment
    Service     = "generated-resume-storage"
    ManagedBy   = "Terraform"
  }
}


# ============================================================
# INTERVIEW AUDIO BUCKET
# ============================================================

resource "aws_s3_bucket" "interview_audio" {
  bucket = "${var.project_name}-${var.environment}-interview-audio-${var.bucket_suffix}"

  force_destroy = var.force_destroy

  tags = {
    Name        = "${var.project_name}-${var.environment}-interview-audio"
    Project     = var.project_name
    Environment = var.environment
    Service     = "interview-audio-storage"
    ManagedBy   = "Terraform"
  }
}


# ============================================================
# INTERVIEW REPORT BUCKET
# ============================================================

resource "aws_s3_bucket" "interview_reports" {
  bucket = "${var.project_name}-${var.environment}-interview-reports-${var.bucket_suffix}"

  force_destroy = var.force_destroy

  tags = {
    Name        = "${var.project_name}-${var.environment}-interview-reports"
    Project     = var.project_name
    Environment = var.environment
    Service     = "interview-report-storage"
    ManagedBy   = "Terraform"
  }
}


# ============================================================
# TEMPORARY STORAGE BUCKET
# ============================================================

resource "aws_s3_bucket" "temporary" {
  bucket = "${var.project_name}-${var.environment}-temporary-${var.bucket_suffix}"

  force_destroy = var.force_destroy

  tags = {
    Name        = "${var.project_name}-${var.environment}-temporary"
    Project     = var.project_name
    Environment = var.environment
    Service     = "temporary-storage"
    ManagedBy   = "Terraform"
  }
}


# ============================================================
# BLOCK PUBLIC ACCESS
# ============================================================

resource "aws_s3_bucket_public_access_block" "resumes" {
  bucket = aws_s3_bucket.resumes.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}


resource "aws_s3_bucket_public_access_block" "generated_resumes" {
  bucket = aws_s3_bucket.generated_resumes.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}


resource "aws_s3_bucket_public_access_block" "interview_audio" {
  bucket = aws_s3_bucket.interview_audio.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}


resource "aws_s3_bucket_public_access_block" "interview_reports" {
  bucket = aws_s3_bucket.interview_reports.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}


resource "aws_s3_bucket_public_access_block" "temporary" {
  bucket = aws_s3_bucket.temporary.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}


# ============================================================
# VERSIONING
# ============================================================

resource "aws_s3_bucket_versioning" "resumes" {
  bucket = aws_s3_bucket.resumes.id

  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Suspended"
  }
}


resource "aws_s3_bucket_versioning" "generated_resumes" {
  bucket = aws_s3_bucket.generated_resumes.id

  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Suspended"
  }
}


resource "aws_s3_bucket_versioning" "interview_audio" {
  bucket = aws_s3_bucket.interview_audio.id

  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Suspended"
  }
}


resource "aws_s3_bucket_versioning" "interview_reports" {
  bucket = aws_s3_bucket.interview_reports.id

  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Suspended"
  }
}


resource "aws_s3_bucket_versioning" "temporary" {
  bucket = aws_s3_bucket.temporary.id

  versioning_configuration {
    status = "Enabled"
  }
}


# ============================================================
# SERVER-SIDE ENCRYPTION
# ============================================================

resource "aws_s3_bucket_server_side_encryption_configuration" "resumes" {
  bucket = aws_s3_bucket.resumes.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = var.kms_key_arn != "" ? "aws:kms" : "AES256"
      kms_master_key_id = var.kms_key_arn != "" ? var.kms_key_arn : null
    }

    bucket_key_enabled = var.kms_key_arn != ""
  }
}


resource "aws_s3_bucket_server_side_encryption_configuration" "generated_resumes" {
  bucket = aws_s3_bucket.generated_resumes.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = var.kms_key_arn != "" ? "aws:kms" : "AES256"
      kms_master_key_id = var.kms_key_arn != "" ? var.kms_key_arn : null
    }

    bucket_key_enabled = var.kms_key_arn != ""
  }
}


resource "aws_s3_bucket_server_side_encryption_configuration" "interview_audio" {
  bucket = aws_s3_bucket.interview_audio.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = var.kms_key_arn != "" ? "aws:kms" : "AES256"
      kms_master_key_id = var.kms_key_arn != "" ? var.kms_key_arn : null
    }

    bucket_key_enabled = var.kms_key_arn != ""
  }
}


resource "aws_s3_bucket_server_side_encryption_configuration" "interview_reports" {
  bucket = aws_s3_bucket.interview_reports.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = var.kms_key_arn != "" ? "aws:kms" : "AES256"
      kms_master_key_id = var.kms_key_arn != "" ? var.kms_key_arn : null
    }

    bucket_key_enabled = var.kms_key_arn != ""
  }
}


resource "aws_s3_bucket_server_side_encryption_configuration" "temporary" {
  bucket = aws_s3_bucket.temporary.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = var.kms_key_arn != "" ? "aws:kms" : "AES256"
      kms_master_key_id = var.kms_key_arn != "" ? var.kms_key_arn : null
    }

    bucket_key_enabled = var.kms_key_arn != ""
  }
}


# ============================================================
# LIFECYCLE - RESUMES
# ============================================================

resource "aws_s3_bucket_lifecycle_configuration" "resumes" {
  bucket = aws_s3_bucket.resumes.id

  rule {
    id     = "resume-retention"
    status = "Enabled"

    filter {
      prefix = ""
    }

    noncurrent_version_expiration {
      noncurrent_days = 90
    }
  }
}


# ============================================================
# LIFECYCLE - GENERATED RESUMES
# ============================================================

resource "aws_s3_bucket_lifecycle_configuration" "generated_resumes" {
  bucket = aws_s3_bucket.generated_resumes.id

  rule {
    id     = "generated-resume-retention"
    status = "Enabled"

    filter {
      prefix = ""
    }

    noncurrent_version_expiration {
      noncurrent_days = 90
    }
  }
}


# ============================================================
# LIFECYCLE - INTERVIEW AUDIO
# ============================================================

resource "aws_s3_bucket_lifecycle_configuration" "interview_audio" {
  bucket = aws_s3_bucket.interview_audio.id

  rule {
    id     = "interview-audio-retention"
    status = "Enabled"

    filter {
      prefix = ""
    }

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    noncurrent_version_expiration {
      noncurrent_days = 90
    }
  }
}


# ============================================================
# LIFECYCLE - INTERVIEW REPORTS
# ============================================================

resource "aws_s3_bucket_lifecycle_configuration" "interview_reports" {
  bucket = aws_s3_bucket.interview_reports.id

  rule {
    id     = "interview-report-retention"
    status = "Enabled"

    filter {
      prefix = ""
    }

    transition {
      days          = 90
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 180
      storage_class = "GLACIER"
    }

    noncurrent_version_expiration {
      noncurrent_days = 180
    }
  }
}


# ============================================================
# LIFECYCLE - TEMPORARY FILES
# ============================================================

resource "aws_s3_bucket_lifecycle_configuration" "temporary" {
  bucket = aws_s3_bucket.temporary.id

  rule {
    id     = "temporary-file-cleanup"
    status = "Enabled"

    filter {
      prefix = ""
    }

    expiration {
      days = var.temporary_file_retention_days
    }

    noncurrent_version_expiration {
      noncurrent_days = 7
    }
  }
}


# ============================================================
# OWNERSHIP CONTROLS
# ============================================================

resource "aws_s3_bucket_ownership_controls" "resumes" {
  bucket = aws_s3_bucket.resumes.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}


resource "aws_s3_bucket_ownership_controls" "generated_resumes" {
  bucket = aws_s3_bucket.generated_resumes.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}


resource "aws_s3_bucket_ownership_controls" "interview_audio" {
  bucket = aws_s3_bucket.interview_audio.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}


resource "aws_s3_bucket_ownership_controls" "interview_reports" {
  bucket = aws_s3_bucket.interview_reports.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}


resource "aws_s3_bucket_ownership_controls" "temporary" {
  bucket = aws_s3_bucket.temporary.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}


# ============================================================
# CORS - RESUME BUCKET
# ============================================================

resource "aws_s3_bucket_cors_configuration" "resumes" {
  bucket = aws_s3_bucket.resumes.id

  cors_rule {
    allowed_headers = ["*"]

    allowed_methods = [
      "GET",
      "PUT",
      "POST",
      "HEAD"
    ]

    allowed_origins = var.allowed_origins

    expose_headers = [
      "ETag"
    ]

    max_age_seconds = 3600
  }
}


# ============================================================
# CORS - GENERATED RESUME BUCKET
# ============================================================

resource "aws_s3_bucket_cors_configuration" "generated_resumes" {
  bucket = aws_s3_bucket.generated_resumes.id

  cors_rule {
    allowed_headers = ["*"]

    allowed_methods = [
      "GET",
      "PUT",
      "HEAD"
    ]

    allowed_origins = var.allowed_origins

    expose_headers = [
      "ETag"
    ]

    max_age_seconds = 3600
  }
}


# ============================================================
# CORS - INTERVIEW AUDIO
# ============================================================

resource "aws_s3_bucket_cors_configuration" "interview_audio" {
  bucket = aws_s3_bucket.interview_audio.id

  cors_rule {
    allowed_headers = ["*"]

    allowed_methods = [
      "GET",
      "PUT",
      "POST",
      "HEAD"
    ]

    allowed_origins = var.allowed_origins

    expose_headers = [
      "ETag"
    ]

    max_age_seconds = 3600
  }
}


# ============================================================
# CORS - INTERVIEW REPORTS
# ============================================================

resource "aws_s3_bucket_cors_configuration" "interview_reports" {
  bucket = aws_s3_bucket.interview_reports.id

  cors_rule {
    allowed_headers = ["*"]

    allowed_methods = [
      "GET",
      "HEAD"
    ]

    allowed_origins = var.allowed_origins

    expose_headers = [
      "ETag"
    ]

    max_age_seconds = 3600
  }
}


# ============================================================
# CORS - TEMPORARY BUCKET
# ============================================================

resource "aws_s3_bucket_cors_configuration" "temporary" {
  bucket = aws_s3_bucket.temporary.id

  cors_rule {
    allowed_headers = ["*"]

    allowed_methods = [
      "GET",
      "PUT",
      "POST",
      "HEAD"
    ]

    allowed_origins = var.allowed_origins

    expose_headers = [
      "ETag"
    ]

    max_age_seconds = 3600
  }
}