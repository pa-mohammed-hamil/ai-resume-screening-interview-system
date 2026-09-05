# Project scaffold file
"""
genai/copilot/actions.py

Recruiter Copilot Actions
=========================

Defines safe, structured actions that the Recruiter Copilot can
request or execute.

Responsibilities:

- Define supported copilot actions
- Validate action parameters
- Check permissions
- Dispatch actions to registered handlers
- Return standardized action results
- Prevent arbitrary function execution

Important:
This module should NOT allow an LLM to directly execute arbitrary
Python functions.

Actual database mutations should remain inside backend services.

Architecture:

    Copilot
       │
       ▼
    actions.py
       │
       ├── Validate action
       ├── Validate parameters
       ├── Check permission
       └── Dispatch handler
              │
              ▼
        Backend service
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional


logger = logging.getLogger(__name__)


# ============================================================================
# TYPES
# ============================================================================

ActionHandler = Callable[..., Awaitable[Any]]


class ActionStatus(str, Enum):
    """
    Standard action execution statuses.
    """

    SUCCESS = "success"
    FAILED = "failed"
    REJECTED = "rejected"
    REQUIRES_CONFIRMATION = "requires_confirmation"


class ActionPermission(str, Enum):
    """
    Permission levels for copilot actions.
    """

    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


# ============================================================================
# ACTION DATA CLASSES
# ============================================================================


@dataclass
class ActionRequest:
    """
    Action requested by the copilot.
    """

    action: str

    parameters: Dict[str, Any] = field(
        default_factory=dict
    )

    user_id: Optional[str] = None

    organization_id: Optional[str] = None

    confirmed: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class ActionResult:
    """
    Standardized action result.
    """

    status: ActionStatus

    action: str

    message: str

    data: Dict[str, Any] = field(
        default_factory=dict
    )

    requires_confirmation: bool = False

    warnings: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class ActionDefinition:
    """
    Defines an available copilot action.
    """

    name: str

    description: str

    permission: ActionPermission = ActionPermission.READ

    requires_confirmation: bool = False

    required_parameters: List[str] = field(
        default_factory=list
    )

    optional_parameters: List[str] = field(
        default_factory=list
    )

    handler: Optional[ActionHandler] = None


# ============================================================================
# ACTION REGISTRY
# ============================================================================


class ActionRegistry:
    """
    Registry containing all supported copilot actions.

    Example:

        registry = ActionRegistry()

        registry.register(
            ActionDefinition(
                name="get_candidate",
                description="Retrieve candidate information",
                required_parameters=["candidate_id"],
            )
        )
    """

    def __init__(self) -> None:

        self._actions: Dict[
            str,
            ActionDefinition,
        ] = {}

    # ------------------------------------------------------------------------
    # REGISTER
    # ------------------------------------------------------------------------

    def register(
        self,
        definition: ActionDefinition,
    ) -> None:
        """
        Register an action.
        """

        if not definition.name:
            raise ValueError(
                "Action name cannot be empty."
            )

        if definition.name in self._actions:
            raise ValueError(
                f"Action already registered: "
                f"{definition.name}"
            )

        self._actions[
            definition.name
        ] = definition

        logger.debug(
            "Registered copilot action: %s",
            definition.name,
        )

    # ------------------------------------------------------------------------
    # GET
    # ------------------------------------------------------------------------

    def get(
        self,
        name: str,
    ) -> Optional[ActionDefinition]:
        """
        Retrieve an action definition.
        """

        return self._actions.get(name)

    # ------------------------------------------------------------------------
    # EXISTS
    # ------------------------------------------------------------------------

    def exists(
        self,
        name: str,
    ) -> bool:
        """
        Check whether an action exists.
        """

        return name in self._actions

    # ------------------------------------------------------------------------
    # LIST
    # ------------------------------------------------------------------------

    def list_actions(self) -> List[ActionDefinition]:
        """
        Return all registered actions.
        """

        return list(
            self._actions.values()
        )

    # ------------------------------------------------------------------------
    # SCHEMA
    # ------------------------------------------------------------------------

    def schema(self) -> List[Dict[str, Any]]:
        """
        Return action metadata suitable for an LLM/tool schema.
        """

        return [
            {
                "name": action.name,
                "description": action.description,
                "permission": action.permission.value,
                "requires_confirmation": (
                    action.requires_confirmation
                ),
                "required_parameters": (
                    action.required_parameters
                ),
                "optional_parameters": (
                    action.optional_parameters
                ),
            }
            for action in self._actions.values()
        ]


# ============================================================================
# ACTION EXECUTOR
# ============================================================================


class ActionExecutor:
    """
    Safely validates and executes registered actions.

    The executor never executes arbitrary function names supplied
    by the LLM.
    """

    def __init__(
        self,
        registry: Optional[ActionRegistry] = None,
    ) -> None:

        self.registry = (
            registry or create_default_registry()
        )

    # ------------------------------------------------------------------------
    # EXECUTE
    # ------------------------------------------------------------------------

    async def execute(
        self,
        request: ActionRequest,
        user_permissions: Optional[
            List[str]
        ] = None,
    ) -> ActionResult:
        """
        Execute a registered action.
        """

        action = self.registry.get(
            request.action
        )

        if action is None:

            return ActionResult(
                status=ActionStatus.REJECTED,
                action=request.action,
                message=(
                    f"Unsupported copilot action: "
                    f"{request.action}"
                ),
            )

        validation_error = self._validate_parameters(
            action=action,
            parameters=request.parameters,
        )

        if validation_error:

            return ActionResult(
                status=ActionStatus.REJECTED,
                action=request.action,
                message=validation_error,
            )

        permission_error = self._check_permission(
            action=action,
            user_permissions=user_permissions or [],
        )

        if permission_error:

            return ActionResult(
                status=ActionStatus.REJECTED,
                action=request.action,
                message=permission_error,
            )

        if (
            action.requires_confirmation
            and not request.confirmed
        ):

            return ActionResult(
                status=ActionStatus.REQUIRES_CONFIRMATION,
                action=request.action,
                message=(
                    "This action requires explicit "
                    "user confirmation."
                ),
                requires_confirmation=True,
            )

        if action.handler is None:

            return ActionResult(
                status=ActionStatus.FAILED,
                action=request.action,
                message=(
                    "Action is registered but no handler "
                    "has been configured."
                ),
            )

        try:

            result = await action.handler(
                **request.parameters
            )

            if isinstance(result, ActionResult):
                return result

            return ActionResult(
                status=ActionStatus.SUCCESS,
                action=request.action,
                message=(
                    f"Action '{request.action}' "
                    "completed successfully."
                ),
                data=self._normalize_result(
                    result
                ),
            )

        except Exception as exc:

            logger.exception(
                "Copilot action failed: %s",
                request.action,
            )

            return ActionResult(
                status=ActionStatus.FAILED,
                action=request.action,
                message=(
                    f"Action '{request.action}' "
                    "failed to execute."
                ),
                warnings=[
                    str(exc)
                ],
            )

    # ------------------------------------------------------------------------
    # PARAMETER VALIDATION
    # ------------------------------------------------------------------------

    @staticmethod
    def _validate_parameters(
        action: ActionDefinition,
        parameters: Dict[str, Any],
    ) -> Optional[str]:
        """
        Validate required parameters.
        """

        if not isinstance(parameters, dict):

            return (
                "Action parameters must be a dictionary."
            )

        missing = [
            parameter
            for parameter in action.required_parameters
            if parameter not in parameters
            or parameters[parameter] is None
        ]

        if missing:

            return (
                "Missing required parameters: "
                + ", ".join(missing)
            )

        allowed = set(
            action.required_parameters
            + action.optional_parameters
        )

        unknown = [
            key
            for key in parameters
            if key not in allowed
        ]

        if unknown:

            return (
                "Unknown action parameters: "
                + ", ".join(unknown)
            )

        return None

    # ------------------------------------------------------------------------
    # PERMISSION CHECK
    # ------------------------------------------------------------------------

    @staticmethod
    def _check_permission(
        action: ActionDefinition,
        user_permissions: List[str],
    ) -> Optional[str]:
        """
        Check whether the current user has permission
        to execute the action.
        """

        required = action.permission.value

        if required == ActionPermission.READ.value:

            if (
                "read"
                not in user_permissions
                and "admin"
                not in user_permissions
            ):
                return (
                    "User does not have read permission."
                )

        elif required == ActionPermission.WRITE.value:

            if (
                "write"
                not in user_permissions
                and "admin"
                not in user_permissions
            ):
                return (
                    "User does not have write permission."
                )

        elif required == ActionPermission.ADMIN.value:

            if "admin" not in user_permissions:

                return (
                    "User does not have admin permission."
                )

        return None

    # ------------------------------------------------------------------------
    # RESULT NORMALIZATION
    # ------------------------------------------------------------------------

    @staticmethod
    def _normalize_result(
        result: Any,
    ) -> Dict[str, Any]:
        """
        Normalize handler output.
        """

        if result is None:
            return {}

        if isinstance(result, dict):
            return result

        if hasattr(result, "model_dump"):

            return result.model_dump()

        if hasattr(result, "dict"):

            return result.dict()

        return {
            "result": result
        }


# ============================================================================
# DEFAULT HANDLERS
# ============================================================================


async def search_candidates(
    query: Optional[str] = None,
    job_id: Optional[str] = None,
    limit: int = 20,
) -> Dict[str, Any]:
    """
    Search candidates.

    In production, replace this placeholder with:

        CandidateService.search_candidates(...)
    """

    limit = max(
        1,
        min(limit, 100),
    )

    return {
        "query": query,
        "job_id": job_id,
        "limit": limit,
        "candidates": [],
        "message": (
            "Candidate search handler is ready "
            "for backend service integration."
        ),
    }


async def get_candidate(
    candidate_id: str,
) -> Dict[str, Any]:
    """
    Retrieve a candidate.

    Replace with CandidateService in production.
    """

    return {
        "candidate_id": candidate_id,
        "candidate": None,
        "message": (
            "Candidate retrieval handler is ready "
            "for backend service integration."
        ),
    }


async def get_job(
    job_id: str,
) -> Dict[str, Any]:
    """
    Retrieve a job.

    Replace with JobService in production.
    """

    return {
        "job_id": job_id,
        "job": None,
        "message": (
            "Job retrieval handler is ready "
            "for backend service integration."
        ),
    }


async def get_resume(
    resume_id: str,
) -> Dict[str, Any]:
    """
    Retrieve a resume.

    Replace with ResumeService in production.
    """

    return {
        "resume_id": resume_id,
        "resume": None,
        "message": (
            "Resume retrieval handler is ready "
            "for backend service integration."
        ),
    }


async def get_interview(
    interview_id: str,
) -> Dict[str, Any]:
    """
    Retrieve interview information.

    Replace with InterviewService in production.
    """

    return {
        "interview_id": interview_id,
        "interview": None,
        "message": (
            "Interview retrieval handler is ready "
            "for backend service integration."
        ),
    }


async def get_analytics(
    metric: Optional[str] = None,
    job_id: Optional[str] = None,
    days: int = 30,
) -> Dict[str, Any]:
    """
    Retrieve recruitment analytics.

    Replace with AnalyticsService in production.
    """

    days = max(
        1,
        min(days, 365),
    )

    return {
        "metric": metric,
        "job_id": job_id,
        "days": days,
        "analytics": {},
        "message": (
            "Analytics handler is ready "
            "for backend service integration."
        ),
    }


async def shortlist_candidate(
    candidate_id: str,
    job_id: str,
) -> Dict[str, Any]:
    """
    Shortlist a candidate.

    This is a write operation and should be explicitly confirmed.
    """

    return {
        "candidate_id": candidate_id,
        "job_id": job_id,
        "status": "shortlisted",
        "message": (
            "Candidate shortlist handler is ready "
            "for backend service integration."
        ),
    }


async def reject_candidate(
    candidate_id: str,
    job_id: str,
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Reject a candidate.

    This is a sensitive write operation and requires confirmation.
    """

    return {
        "candidate_id": candidate_id,
        "job_id": job_id,
        "reason": reason,
        "status": "rejection_pending",
        "message": (
            "Candidate rejection handler is ready "
            "for backend service integration."
        ),
    }


async def schedule_interview(
    candidate_id: str,
    job_id: str,
    scheduled_at: str,
) -> Dict[str, Any]:
    """
    Schedule an interview.

    This is a write operation and requires confirmation.
    """

    return {
        "candidate_id": candidate_id,
        "job_id": job_id,
        "scheduled_at": scheduled_at,
        "status": "scheduled",
        "message": (
            "Interview scheduling handler is ready "
            "for backend service integration."
        ),
    }


async def generate_interview_questions(
    job_id: str,
    candidate_id: Optional[str] = None,
    count: int = 5,
) -> Dict[str, Any]:
    """
    Generate interview questions.

    Actual generation should be delegated to InterviewAgent.
    """

    count = max(
        1,
        min(count, 20),
    )

    return {
        "job_id": job_id,
        "candidate_id": candidate_id,
        "count": count,
        "questions": [],
        "message": (
            "Interview question action is ready "
            "for InterviewAgent integration."
        ),
    }


async def analyze_resume(
    resume_id: str,
    job_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Analyze a resume.
    """

    return {
        "resume_id": resume_id,
        "job_id": job_id,
        "analysis": {},
        "message": (
            "Resume analysis action is ready "
            "for ResumeAgent integration."
        ),
    }


async def generate_report(
    report_type: str,
    job_id: Optional[str] = None,
    candidate_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate a recruitment report.
    """

    return {
        "report_type": report_type,
        "job_id": job_id,
        "candidate_id": candidate_id,
        "report": None,
        "message": (
            "Report generation action is ready "
            "for report service integration."
        ),
    }


# ============================================================================
# DEFAULT REGISTRY
# ============================================================================


def create_default_registry() -> ActionRegistry:
    """
    Create the default recruiter-copilot action registry.
    """

    registry = ActionRegistry()

    # ------------------------------------------------------------------------
    # READ ACTIONS
    # ------------------------------------------------------------------------

    registry.register(
        ActionDefinition(
            name="search_candidates",
            description=(
                "Search candidates using recruiter-supplied "
                "criteria."
            ),
            permission=ActionPermission.READ,
            required_parameters=[],
            optional_parameters=[
                "query",
                "job_id",
                "limit",
            ],
            handler=search_candidates,
        )
    )

    registry.register(
        ActionDefinition(
            name="get_candidate",
            description=(
                "Retrieve information about a specific candidate."
            ),
            permission=ActionPermission.READ,
            required_parameters=[
                "candidate_id"
            ],
            handler=get_candidate,
        )
    )

    registry.register(
        ActionDefinition(
            name="get_job",
            description=(
                "Retrieve information about a job."
            ),
            permission=ActionPermission.READ,
            required_parameters=[
                "job_id"
            ],
            handler=get_job,
        )
    )

    registry.register(
        ActionDefinition(
            name="get_resume",
            description=(
                "Retrieve a candidate resume."
            ),
            permission=ActionPermission.READ,
            required_parameters=[
                "resume_id"
            ],
            handler=get_resume,
        )
    )

    registry.register(
        ActionDefinition(
            name="get_interview",
            description=(
                "Retrieve interview information."
            ),
            permission=ActionPermission.READ,
            required_parameters=[
                "interview_id"
            ],
            handler=get_interview,
        )
    )

    registry.register(
        ActionDefinition(
            name="get_analytics",
            description=(
                "Retrieve recruitment analytics."
            ),
            permission=ActionPermission.READ,
            required_parameters=[],
            optional_parameters=[
                "metric",
                "job_id",
                "days",
            ],
            handler=get_analytics,
        )
    )

    # ------------------------------------------------------------------------
    # AI ACTIONS
    # ------------------------------------------------------------------------

    registry.register(
        ActionDefinition(
            name="generate_interview_questions",
            description=(
                "Generate job-relevant interview questions."
            ),
            permission=ActionPermission.READ,
            required_parameters=[
                "job_id"
            ],
            optional_parameters=[
                "candidate_id",
                "count",
            ],
            handler=generate_interview_questions,
        )
    )

    registry.register(
        ActionDefinition(
            name="analyze_resume",
            description=(
                "Analyze a candidate resume against a job."
            ),
            permission=ActionPermission.READ,
            required_parameters=[
                "resume_id"
            ],
            optional_parameters=[
                "job_id"
            ],
            handler=analyze_resume,
        )
    )

    # ------------------------------------------------------------------------
    # WRITE ACTIONS
    # ------------------------------------------------------------------------

    registry.register(
        ActionDefinition(
            name="shortlist_candidate",
            description=(
                "Move a candidate into the shortlist."
            ),
            permission=ActionPermission.WRITE,
            requires_confirmation=True,
            required_parameters=[
                "candidate_id",
                "job_id",
            ],
            handler=shortlist_candidate,
        )
    )

    registry.register(
        ActionDefinition(
            name="reject_candidate",
            description=(
                "Reject a candidate from a job pipeline."
            ),
            permission=ActionPermission.WRITE,
            requires_confirmation=True,
            required_parameters=[
                "candidate_id",
                "job_id",
            ],
            optional_parameters=[
                "reason"
            ],
            handler=reject_candidate,
        )
    )

    registry.register(
        ActionDefinition(
            name="schedule_interview",
            description=(
                "Schedule an interview for a candidate."
            ),
            permission=ActionPermission.WRITE,
            requires_confirmation=True,
            required_parameters=[
                "candidate_id",
                "job_id",
                "scheduled_at",
            ],
            handler=schedule_interview,
        )
    )

    registry.register(
        ActionDefinition(
            name="generate_report",
            description=(
                "Generate a recruitment report."
            ),
            permission=ActionPermission.WRITE,
            requires_confirmation=True,
            required_parameters=[
                "report_type"
            ],
            optional_parameters=[
                "job_id",
                "candidate_id",
            ],
            handler=generate_report,
        )
    )

    return registry


# ============================================================================
# GLOBAL DEFAULT EXECUTOR
# ============================================================================


default_action_registry = create_default_registry()

default_action_executor = ActionExecutor(
    registry=default_action_registry
)


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================


def get_available_actions() -> List[Dict[str, Any]]:
    """
    Return available copilot actions.
    """

    return default_action_registry.schema()


async def execute_action(
    action: str,
    parameters: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    organization_id: Optional[str] = None,
    confirmed: bool = False,
    user_permissions: Optional[List[str]] = None,
) -> ActionResult:
    """
    Convenience function for executing a copilot action.
    """

    request = ActionRequest(
        action=action,
        parameters=parameters or {},
        user_id=user_id,
        organization_id=organization_id,
        confirmed=confirmed,
    )

    return await default_action_executor.execute(
        request=request,
        user_permissions=user_permissions or [],
    )