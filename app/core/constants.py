"""
Application-wide constants.

Keep reusable fixed values here instead of scattering
magic strings and numbers throughout the codebase.
"""

# ============================================================
# Application
# ============================================================

APP_NAME = "AI Resume Screening & Interview System"
APP_VERSION = "1.0.0"
API_V1_PREFIX = "/api/v1"


# ============================================================
# User Roles
# ============================================================

ROLE_ADMIN = "admin"
ROLE_RECRUITER = "recruiter"
ROLE_HIRING_MANAGER = "hiring_manager"
ROLE_INTERVIEWER = "interviewer"
ROLE_CANDIDATE = "candidate"

USER_ROLES = (
    ROLE_ADMIN,
    ROLE_RECRUITER,
    ROLE_HIRING_MANAGER,
    ROLE_INTERVIEWER,
    ROLE_CANDIDATE,
)


# ============================================================
# Resume
# ============================================================

RESUME_STATUS_UPLOADED = "uploaded"
RESUME_STATUS_PROCESSING = "processing"
RESUME_STATUS_COMPLETED = "completed"
RESUME_STATUS_FAILED = "failed"

RESUME_STATUSES = (
    RESUME_STATUS_UPLOADED,
    RESUME_STATUS_PROCESSING,
    RESUME_STATUS_COMPLETED,
    RESUME_STATUS_FAILED,
)

# Supported resume formats
ALLOWED_RESUME_EXTENSIONS = {
    ".pdf",
    ".docx",
}

ALLOWED_RESUME_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

MAX_RESUME_FILE_SIZE_MB = 10
MAX_RESUME_FILE_SIZE_BYTES = MAX_RESUME_FILE_SIZE_MB * 1024 * 1024


# ============================================================
# Job
# ============================================================

JOB_STATUS_DRAFT = "draft"
JOB_STATUS_OPEN = "open"
JOB_STATUS_CLOSED = "closed"
JOB_STATUS_ARCHIVED = "archived"

JOB_STATUSES = (
    JOB_STATUS_DRAFT,
    JOB_STATUS_OPEN,
    JOB_STATUS_CLOSED,
    JOB_STATUS_ARCHIVED,
)


# ============================================================
# Candidate
# ============================================================

CANDIDATE_STATUS_NEW = "new"
CANDIDATE_STATUS_SCREENING = "screening"
CANDIDATE_STATUS_SHORTLISTED = "shortlisted"
CANDIDATE_STATUS_INTERVIEW = "interview"
CANDIDATE_STATUS_REJECTED = "rejected"
CANDIDATE_STATUS_HIRED = "hired"

CANDIDATE_STATUSES = (
    CANDIDATE_STATUS_NEW,
    CANDIDATE_STATUS_SCREENING,
    CANDIDATE_STATUS_SHORTLISTED,
    CANDIDATE_STATUS_INTERVIEW,
    CANDIDATE_STATUS_REJECTED,
    CANDIDATE_STATUS_HIRED,
)


# ============================================================
# Interview
# ============================================================

INTERVIEW_STATUS_SCHEDULED = "scheduled"
INTERVIEW_STATUS_IN_PROGRESS = "in_progress"
INTERVIEW_STATUS_COMPLETED = "completed"
INTERVIEW_STATUS_CANCELLED = "cancelled"

INTERVIEW_STATUSES = (
    INTERVIEW_STATUS_SCHEDULED,
    INTERVIEW_STATUS_IN_PROGRESS,
    INTERVIEW_STATUS_COMPLETED,
    INTERVIEW_STATUS_CANCELLED,
)


# ============================================================
# Interview Types
# ============================================================

INTERVIEW_TYPE_TECHNICAL = "technical"
INTERVIEW_TYPE_BEHAVIORAL = "behavioral"
INTERVIEW_TYPE_MIXED = "mixed"
INTERVIEW_TYPE_CODING = "coding"

INTERVIEW_TYPES = (
    INTERVIEW_TYPE_TECHNICAL,
    INTERVIEW_TYPE_BEHAVIORAL,
    INTERVIEW_TYPE_MIXED,
    INTERVIEW_TYPE_CODING,
)


# ============================================================
# Difficulty Levels
# ============================================================

DIFFICULTY_EASY = "easy"
DIFFICULTY_MEDIUM = "medium"
DIFFICULTY_HARD = "hard"

DIFFICULTY_LEVELS = (
    DIFFICULTY_EASY,
    DIFFICULTY_MEDIUM,
    DIFFICULTY_HARD,
)


# ============================================================
# AI / Matching
# ============================================================

MATCHING_METHOD_KEYWORD = "keyword"
MATCHING_METHOD_SEMANTIC = "semantic"
MATCHING_METHOD_HYBRID = "hybrid"

MATCHING_METHODS = (
    MATCHING_METHOD_KEYWORD,
    MATCHING_METHOD_SEMANTIC,
    MATCHING_METHOD_HYBRID,
)


# ============================================================
# Score Thresholds
# ============================================================

SCORE_MIN = 0
SCORE_MAX = 100

MATCH_SCORE_STRONG = 80
MATCH_SCORE_GOOD = 65
MATCH_SCORE_MODERATE = 50
MATCH_SCORE_LOW = 0


# ============================================================
# Pagination
# ============================================================

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 20

MIN_PAGE_SIZE = 1
MAX_PAGE_SIZE = 100


# ============================================================
# File Storage
# ============================================================

STORAGE_RESUMES = "storage/resumes"
STORAGE_GENERATED_RESUMES = "storage/generated_resumes"
STORAGE_INTERVIEW_AUDIO = "storage/interview_audio"
STORAGE_INTERVIEW_REPORTS = "storage/interview_reports"
STORAGE_TEMPORARY = "storage/temporary"


# ============================================================
# AI Processing
# ============================================================

MAX_TEXT_LENGTH = 50_000
MAX_RESUME_PAGES = 10

DEFAULT_EMBEDDING_DIMENSION = 1536

DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50


# ============================================================
# Celery Tasks
# ============================================================

TASK_RESUME_PROCESSING = "resume.process"
TASK_EMBEDDING_GENERATION = "embedding.generate"
TASK_INTERVIEW_PROCESSING = "interview.process"
TASK_REPORT_GENERATION = "report.generate"


# ============================================================
# API Messages
# ============================================================

MSG_RESUME_UPLOADED = "Resume uploaded successfully."
MSG_RESUME_PROCESSING = "Resume processing started."
MSG_RESUME_NOT_FOUND = "Resume not found."

MSG_JOB_NOT_FOUND = "Job not found."
MSG_CANDIDATE_NOT_FOUND = "Candidate not found."
MSG_INTERVIEW_NOT_FOUND = "Interview not found."

MSG_UNAUTHORIZED = "Authentication required."
MSG_FORBIDDEN = "You do not have permission to perform this action."


# ============================================================
# HTTP Headers
# ============================================================

HEADER_AUTHORIZATION = "Authorization"
HEADER_CONTENT_TYPE = "Content-Type"
HEADER_REQUEST_ID = "X-Request-ID"


# ============================================================
# Security
# ============================================================

ACCESS_TOKEN_TYPE = "bearer"

PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128

AUTH_HEADER_PREFIX = "Bearer"


# ============================================================
# Environment Names
# ============================================================

ENV_DEVELOPMENT = "development"
ENV_TESTING = "testing"
ENV_STAGING = "staging"
ENV_PRODUCTION = "production"

ENVIRONMENTS = (
    ENV_DEVELOPMENT,
    ENV_TESTING,
    ENV_STAGING,
    ENV_PRODUCTION,
)