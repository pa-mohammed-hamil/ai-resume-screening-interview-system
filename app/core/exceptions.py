"""
Application-specific exceptions.

Centralized exception definitions for the
AI Resume Screening & Interview System.
"""

from typing import Any, Dict, Optional


# ---------------------------------------------------------------------------
# Base Application Exception
# ---------------------------------------------------------------------------

class AppException(Exception):
    """
    Base exception for all application-specific errors.
    """

    status_code: int = 500
    code: str = "APPLICATION_ERROR"
    message: str = "An application error occurred."

    def __init__(
        self,
        message: Optional[str] = None,
        *,
        code: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message or self.message
        self.code = code or self.code
        self.status_code = status_code or self.status_code
        self.details = details or {}

        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception into an API-friendly dictionary.
        """

        response = {
            "success": False,
            "error": {
                "code": self.code,
                "message": self.message,
            },
        }

        if self.details:
            response["error"]["details"] = self.details

        return response


# ---------------------------------------------------------------------------
# Authentication Exceptions
# ---------------------------------------------------------------------------

class AuthenticationError(AppException):
    """
    Raised when authentication fails.
    """

    status_code = 401
    code = "AUTHENTICATION_ERROR"
    message = "Authentication failed."


class InvalidCredentialsError(AuthenticationError):
    """
    Raised when email/password credentials are invalid.
    """

    code = "INVALID_CREDENTIALS"
    message = "Invalid email or password."


class InvalidTokenError(AuthenticationError):
    """
    Raised when an authentication token is invalid.
    """

    code = "INVALID_TOKEN"
    message = "Invalid or expired authentication token."


class TokenExpiredError(AuthenticationError):
    """
    Raised when an authentication token has expired.
    """

    code = "TOKEN_EXPIRED"
    message = "Authentication token has expired."


# ---------------------------------------------------------------------------
# Authorization Exceptions
# ---------------------------------------------------------------------------

class AuthorizationError(AppException):
    """
    Raised when a user is authenticated but not authorized.
    """

    status_code = 403
    code = "AUTHORIZATION_ERROR"
    message = "You are not authorized to perform this action."


class PermissionDeniedError(AuthorizationError):
    """
    Raised when a required permission is missing.
    """

    code = "PERMISSION_DENIED"
    message = "You do not have permission to perform this action."


class RoleRequiredError(AuthorizationError):
    """
    Raised when a specific role is required.
    """

    code = "ROLE_REQUIRED"
    message = "You do not have the required role."


# ---------------------------------------------------------------------------
# Resource Exceptions
# ---------------------------------------------------------------------------

class ResourceNotFoundError(AppException):
    """
    Raised when a requested resource does not exist.
    """

    status_code = 404
    code = "RESOURCE_NOT_FOUND"
    message = "Requested resource was not found."


class UserNotFoundError(ResourceNotFoundError):
    """
    Raised when a user does not exist.
    """

    code = "USER_NOT_FOUND"
    message = "User not found."


class ResumeNotFoundError(ResourceNotFoundError):
    """
    Raised when a resume does not exist.
    """

    code = "RESUME_NOT_FOUND"
    message = "Resume not found."


class JobNotFoundError(ResourceNotFoundError):
    """
    Raised when a job does not exist.
    """

    code = "JOB_NOT_FOUND"
    message = "Job not found."


class CandidateNotFoundError(ResourceNotFoundError):
    """
    Raised when a candidate does not exist.
    """

    code = "CANDIDATE_NOT_FOUND"
    message = "Candidate not found."


class InterviewNotFoundError(ResourceNotFoundError):
    """
    Raised when an interview does not exist.
    """

    code = "INTERVIEW_NOT_FOUND"
    message = "Interview not found."


# ---------------------------------------------------------------------------
# Validation Exceptions
# ---------------------------------------------------------------------------

class ValidationError(AppException):
    """
    Raised when business-level validation fails.
    """

    status_code = 422
    code = "VALIDATION_ERROR"
    message = "Validation failed."


class InvalidInputError(ValidationError):
    """
    Raised when user input is invalid.
    """

    code = "INVALID_INPUT"
    message = "Invalid input."


class InvalidFileError(ValidationError):
    """
    Raised when an uploaded file is invalid.
    """

    code = "INVALID_FILE"
    message = "Invalid file."


class UnsupportedFileTypeError(ValidationError):
    """
    Raised when an unsupported file type is uploaded.
    """

    code = "UNSUPPORTED_FILE_TYPE"
    message = "Unsupported file type."


class FileTooLargeError(ValidationError):
    """
    Raised when an uploaded file exceeds the allowed size.
    """

    code = "FILE_TOO_LARGE"
    message = "Uploaded file is too large."


# ---------------------------------------------------------------------------
# Resume Exceptions
# ---------------------------------------------------------------------------

class ResumeProcessingError(AppException):
    """
    Raised when resume processing fails.
    """

    status_code = 422
    code = "RESUME_PROCESSING_ERROR"
    message = "Unable to process the resume."


class ResumeParsingError(ResumeProcessingError):
    """
    Raised when PDF/DOCX parsing fails.
    """

    code = "RESUME_PARSING_ERROR"
    message = "Unable to parse the resume."


class ResumeExtractionError(ResumeProcessingError):
    """
    Raised when information extraction fails.
    """

    code = "RESUME_EXTRACTION_ERROR"
    message = "Unable to extract information from the resume."


class ResumeAnalysisError(ResumeProcessingError):
    """
    Raised when AI resume analysis fails.
    """

    code = "RESUME_ANALYSIS_ERROR"
    message = "Unable to analyze the resume."


# ---------------------------------------------------------------------------
# Job Description Exceptions
# ---------------------------------------------------------------------------

class JobProcessingError(AppException):
    """
    Raised when job description processing fails.
    """

    status_code = 422
    code = "JOB_PROCESSING_ERROR"
    message = "Unable to process the job description."


class JobDescriptionParsingError(JobProcessingError):
    """
    Raised when a job description cannot be parsed.
    """

    code = "JD_PARSING_ERROR"
    message = "Unable to parse the job description."


class RequirementExtractionError(JobProcessingError):
    """
    Raised when job requirements cannot be extracted.
    """

    code = "REQUIREMENT_EXTRACTION_ERROR"
    message = "Unable to extract job requirements."


# ---------------------------------------------------------------------------
# Matching & Ranking Exceptions
# ---------------------------------------------------------------------------

class MatchingError(AppException):
    """
    Raised when candidate-job matching fails.
    """

    status_code = 422
    code = "MATCHING_ERROR"
    message = "Unable to match candidate with job."


class RankingError(AppException):
    """
    Raised when candidate ranking fails.
    """

    status_code = 422
    code = "RANKING_ERROR"
    message = "Unable to rank candidates."


class ScoringError(AppException):
    """
    Raised when candidate/resume scoring fails.
    """

    status_code = 422
    code = "SCORING_ERROR"
    message = "Unable to calculate score."


# ---------------------------------------------------------------------------
# AI / LLM Exceptions
# ---------------------------------------------------------------------------

class AIServiceError(AppException):
    """
    Base exception for AI service failures.
    """

    status_code = 502
    code = "AI_SERVICE_ERROR"
    message = "AI service is currently unavailable."


class LLMError(AIServiceError):
    """
    Raised when an LLM request fails.
    """

    code = "LLM_ERROR"
    message = "Unable to generate an AI response."


class LLMTimeoutError(LLMError):
    """
    Raised when an LLM request times out.
    """

    code = "LLM_TIMEOUT"
    message = "AI service request timed out."


class LLMRateLimitError(LLMError):
    """
    Raised when an AI provider rate limit is reached.
    """

    status_code = 429
    code = "LLM_RATE_LIMIT"
    message = "AI service rate limit exceeded."


class EmbeddingError(AIServiceError):
    """
    Raised when embedding generation fails.
    """

    code = "EMBEDDING_ERROR"
    message = "Unable to generate embeddings."


class VectorStoreError(AIServiceError):
    """
    Raised when vector database operations fail.
    """

    code = "VECTOR_STORE_ERROR"
    message = "Vector search service is unavailable."


# ---------------------------------------------------------------------------
# RAG Exceptions
# ---------------------------------------------------------------------------

class RAGError(AIServiceError):
    """
    Raised when RAG processing fails.
    """

    code = "RAG_ERROR"
    message = "Unable to process the knowledge base."


class DocumentRetrievalError(RAGError):
    """
    Raised when document retrieval fails.
    """

    code = "DOCUMENT_RETRIEVAL_ERROR"
    message = "Unable to retrieve relevant documents."


# ---------------------------------------------------------------------------
# Interview Exceptions
# ---------------------------------------------------------------------------

class InterviewError(AppException):
    """
    Base exception for interview operations.
    """

    status_code = 422
    code = "INTERVIEW_ERROR"
    message = "Interview operation failed."


class QuestionGenerationError(InterviewError):
    """
    Raised when interview question generation fails.
    """

    code = "QUESTION_GENERATION_ERROR"
    message = "Unable to generate interview questions."


class AnswerEvaluationError(InterviewError):
    """
    Raised when an interview answer cannot be evaluated.
    """

    code = "ANSWER_EVALUATION_ERROR"
    message = "Unable to evaluate the interview answer."


class InterviewReportError(InterviewError):
    """
    Raised when an interview report cannot be generated.
    """

    code = "INTERVIEW_REPORT_ERROR"
    message = "Unable to generate the interview report."


class InterviewSessionError(InterviewError):
    """
    Raised when an interview session is invalid.
    """

    code = "INTERVIEW_SESSION_ERROR"
    message = "Invalid interview session."


# ---------------------------------------------------------------------------
# Voice Exceptions
# ---------------------------------------------------------------------------

class VoiceProcessingError(AppException):
    """
    Raised when voice processing fails.
    """

    status_code = 422
    code = "VOICE_PROCESSING_ERROR"
    message = "Unable to process voice data."


class SpeechToTextError(VoiceProcessingError):
    """
    Raised when speech-to-text conversion fails.
    """

    code = "SPEECH_TO_TEXT_ERROR"
    message = "Unable to convert speech to text."


class TextToSpeechError(VoiceProcessingError):
    """
    Raised when text-to-speech conversion fails.
    """

    code = "TEXT_TO_SPEECH_ERROR"
    message = "Unable to generate speech."


# ---------------------------------------------------------------------------
# Database Exceptions
# ---------------------------------------------------------------------------

class DatabaseError(AppException):
    """
    Base database exception.
    """

    status_code = 500
    code = "DATABASE_ERROR"
    message = "A database error occurred."


class DatabaseConnectionError(DatabaseError):
    """
    Raised when the database cannot be reached.
    """

    code = "DATABASE_CONNECTION_ERROR"
    message = "Unable to connect to the database."


class DatabaseQueryError(DatabaseError):
    """
    Raised when a database query fails.
    """

    code = "DATABASE_QUERY_ERROR"
    message = "Database query failed."


class DuplicateResourceError(AppException):
    """
    Raised when a resource already exists.
    """

    status_code = 409
    code = "DUPLICATE_RESOURCE"
    message = "Resource already exists."


class EmailAlreadyExistsError(DuplicateResourceError):
    """
    Raised when a registered email already exists.
    """

    code = "EMAIL_ALREADY_EXISTS"
    message = "An account with this email already exists."


# ---------------------------------------------------------------------------
# Storage Exceptions
# ---------------------------------------------------------------------------

class StorageError(AppException):
    """
    Base file-storage exception.
    """

    status_code = 500
    code = "STORAGE_ERROR"
    message = "Storage operation failed."


class FileUploadError(StorageError):
    """
    Raised when file upload fails.
    """

    code = "FILE_UPLOAD_ERROR"
    message = "Unable to upload file."


class FileDownloadError(StorageError):
    """
    Raised when file download fails.
    """

    code = "FILE_DOWNLOAD_ERROR"
    message = "Unable to download file."


class FileDeleteError(StorageError):
    """
    Raised when file deletion fails.
    """

    code = "FILE_DELETE_ERROR"
    message = "Unable to delete file."


# ---------------------------------------------------------------------------
# External Service Exceptions
# ---------------------------------------------------------------------------

class ExternalServiceError(AppException):
    """
    Base exception for external service failures.
    """

    status_code = 502
    code = "EXTERNAL_SERVICE_ERROR"
    message = "External service is unavailable."


class EmailServiceError(ExternalServiceError):
    """
    Raised when email service fails.
    """

    code = "EMAIL_SERVICE_ERROR"
    message = "Unable to send email."


class AWSServiceError(ExternalServiceError):
    """
    Raised when AWS service operations fail.
    """

    code = "AWS_SERVICE_ERROR"
    message = "AWS service operation failed."


# ---------------------------------------------------------------------------
# Rate Limiting
# ---------------------------------------------------------------------------

class RateLimitError(AppException):
    """
    Raised when an API rate limit is exceeded.
    """

    status_code = 429
    code = "RATE_LIMIT_EXCEEDED"
    message = "Too many requests. Please try again later."


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def exception_response(
    exc: AppException,
) -> Dict[str, Any]:
    """
    Convert an AppException into a standardized response.
    """

    return exc.to_dict()
