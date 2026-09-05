# Project scaffold file
"""
Response parsing and validation utilities for LLM responses.

Responsibilities:
- Parse raw LLM text
- Extract JSON from markdown/code fences
- Validate JSON structure
- Validate required fields
- Normalize common LLM response formats
- Provide safe parsing helpers
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Type,
    TypeVar,
)


# ============================================================================
# Exceptions
# ============================================================================


class ResponseParserError(Exception):
    """Base exception for response parsing errors."""


class InvalidJSONError(ResponseParserError):
    """Raised when an LLM response cannot be parsed as JSON."""


class InvalidResponseError(ResponseParserError):
    """Raised when an LLM response has an invalid structure."""


class MissingFieldError(ResponseParserError):
    """Raised when required fields are missing."""


class FieldTypeError(ResponseParserError):
    """Raised when a field has an unexpected type."""


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class ParsedResponse:
    """Normalized parsed LLM response."""

    data: Dict[str, Any]

    raw_text: str

    cleaned_text: str

    warnings: List[str] = field(
        default_factory=list
    )

    @property
    def is_valid(self) -> bool:
        return bool(self.data)


@dataclass
class ValidationResult:
    """Result of schema validation."""

    valid: bool

    data: Dict[str, Any]

    errors: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )


# ============================================================================
# Generic Type
# ============================================================================


T = TypeVar("T")


# ============================================================================
# JSON Extraction
# ============================================================================


def clean_response(text: str) -> str:
    """
    Clean common formatting added by LLMs.

    Handles:
    - whitespace
    - markdown JSON fences
    - generic markdown code fences
    - leading/trailing text where possible
    """

    if not isinstance(text, str):
        raise InvalidResponseError(
            "LLM response must be a string."
        )

    cleaned = text.strip()

    if not cleaned:
        raise InvalidResponseError(
            "LLM response is empty."
        )

    # Remove common markdown code fences.
    cleaned = remove_code_fences(
        cleaned
    )

    return cleaned.strip()


def remove_code_fences(
    text: str,
) -> str:
    """
    Remove Markdown code fences.

    Examples:

        ```json
        {"score": 90}
        ```

    becomes:

        {"score": 90}
    """

    text = text.strip()

    pattern = re.compile(
        r"^```(?:json|JSON|javascript|js)?\s*"
        r"(.*?)"
        r"\s*```$",
        re.DOTALL,
    )

    match = pattern.match(
        text
    )

    if match:
        return match.group(1).strip()

    return text


def extract_json_object(
    text: str,
) -> str:
    """
    Extract the first complete JSON object from text.

    This is useful when a model returns:

        Here is the result:
        {"score": 85}

    """

    cleaned = clean_response(
        text
    )

    # Already valid JSON.
    try:
        parsed = json.loads(
            cleaned
        )

        if isinstance(
            parsed,
            dict,
        ):
            return cleaned

    except json.JSONDecodeError:
        pass

    start = cleaned.find(
        "{"
    )

    if start == -1:
        raise InvalidJSONError(
            "No JSON object found in LLM response."
        )

    depth = 0
    in_string = False
    escaped = False

    for index in range(
        start,
        len(cleaned),
    ):
        char = cleaned[index]

        if in_string:

            if escaped:
                escaped = False

            elif char == "\\":
                escaped = True

            elif char == '"':
                in_string = False

            continue

        if char == '"':
            in_string = True

        elif char == "{":
            depth += 1

        elif char == "}":
            depth -= 1

            if depth == 0:
                return cleaned[
                    start : index + 1
                ]

    raise InvalidJSONError(
        "Incomplete JSON object in LLM response."
    )


def extract_json_array(
    text: str,
) -> str:
    """
    Extract the first complete JSON array.
    """

    cleaned = clean_response(
        text
    )

    try:
        parsed = json.loads(
            cleaned
        )

        if isinstance(
            parsed,
            list,
        ):
            return cleaned

    except json.JSONDecodeError:
        pass

    start = cleaned.find(
        "["
    )

    if start == -1:
        raise InvalidJSONError(
            "No JSON array found in LLM response."
        )

    depth = 0
    in_string = False
    escaped = False

    for index in range(
        start,
        len(cleaned),
    ):
        char = cleaned[index]

        if in_string:

            if escaped:
                escaped = False

            elif char == "\\":
                escaped = True

            elif char == '"':
                in_string = False

            continue

        if char == '"':
            in_string = True

        elif char == "[":
            depth += 1

        elif char == "]":
            depth -= 1

            if depth == 0:
                return cleaned[
                    start : index + 1
                ]

    raise InvalidJSONError(
        "Incomplete JSON array in LLM response."
    )


# ============================================================================
# JSON Parsing
# ============================================================================


def parse_json(
    text: str,
    *,
    expect_object: bool = True,
) -> Any:
    """
    Parse JSON returned by an LLM.

    Attempts:
    1. Direct JSON parsing
    2. JSON object extraction
    3. JSON array extraction
    """

    cleaned = clean_response(
        text
    )

    # First attempt: direct parsing.
    try:
        result = json.loads(
            cleaned
        )

    except json.JSONDecodeError:

        if expect_object:
            extracted = extract_json_object(
                cleaned
            )
        else:
            extracted = extract_json_array(
                cleaned
            )

        try:
            result = json.loads(
                extracted
            )

        except json.JSONDecodeError as exc:
            raise InvalidJSONError(
                "Unable to parse LLM response as JSON."
            ) from exc

    if expect_object and not isinstance(
        result,
        dict,
    ):
        raise InvalidResponseError(
            "Expected a JSON object."
        )

    if not expect_object and not isinstance(
        result,
        list,
    ):
        raise InvalidResponseError(
            "Expected a JSON array."
        )

    return result


def parse_object(
    text: str,
) -> Dict[str, Any]:
    """
    Parse an LLM response into a JSON object.
    """

    result = parse_json(
        text,
        expect_object=True,
    )

    return result


def parse_array(
    text: str,
) -> List[Any]:
    """
    Parse an LLM response into a JSON array.
    """

    result = parse_json(
        text,
        expect_object=False,
    )

    return result


# ============================================================================
# Response Parsing
# ============================================================================


def parse_response(
    text: str,
    *,
    required_fields: Optional[
        Iterable[str]
    ] = None,
    field_types: Optional[
        Mapping[str, Type[Any]]
    ] = None,
) -> ParsedResponse:
    """
    Parse and validate an LLM JSON response.
    """

    raw_text = text

    cleaned = clean_response(
        text
    )

    data = parse_object(
        cleaned
    )

    warnings: List[str] = []

    if required_fields:
        missing = find_missing_fields(
            data,
            required_fields,
        )

        if missing:
            raise MissingFieldError(
                "Missing required fields: "
                + ", ".join(missing)
            )

    if field_types:
        validate_field_types(
            data,
            field_types,
        )

    return ParsedResponse(
        data=data,
        raw_text=raw_text,
        cleaned_text=cleaned,
        warnings=warnings,
    )


# ============================================================================
# Required Field Validation
# ============================================================================


def find_missing_fields(
    data: Mapping[str, Any],
    required_fields: Iterable[str],
) -> List[str]:
    """
    Return required fields that are missing.

    Nested fields can be specified using dot notation.

    Example:

        candidate.name
    """

    missing = []

    for field_name in required_fields:

        if not has_field(
            data,
            field_name,
        ):
            missing.append(
                field_name
            )

    return missing


def has_field(
    data: Mapping[str, Any],
    field_name: str,
) -> bool:
    """
    Check whether a nested field exists.
    """

    current: Any = data

    for part in field_name.split(
        "."
    ):

        if not isinstance(
            current,
            Mapping,
        ):
            return False

        if part not in current:
            return False

        current = current[
            part
        ]

    return True


def get_field(
    data: Mapping[str, Any],
    field_name: str,
    default: Any = None,
) -> Any:
    """
    Safely retrieve a nested field.
    """

    current: Any = data

    for part in field_name.split(
        "."
    ):

        if not isinstance(
            current,
            Mapping,
        ):
            return default

        if part not in current:
            return default

        current = current[
            part
        ]

    return current


def require_field(
    data: Mapping[str, Any],
    field_name: str,
) -> Any:
    """
    Retrieve a required field.
    """

    if not has_field(
        data,
        field_name,
    ):
        raise MissingFieldError(
            f"Required field '{field_name}' is missing."
        )

    return get_field(
        data,
        field_name,
    )


# ============================================================================
# Type Validation
# ============================================================================


def validate_field_types(
    data: Mapping[str, Any],
    field_types: Mapping[
        str,
        Type[Any],
    ],
) -> None:
    """
    Validate types for selected fields.

    Example:

        {
            "score": float,
            "strengths": list,
            "recommendation": str
        }
    """

    errors = []

    for field_name, expected_type in field_types.items():

        if not has_field(
            data,
            field_name,
        ):
            continue

        value = get_field(
            data,
            field_name,
        )

        if value is None:
            continue

        # bool is a subclass of int, so explicitly
        # prevent bool from being accepted as int.
        if (
            expected_type is int
            and isinstance(
                value,
                bool,
            )
        ):
            errors.append(
                f"{field_name}: expected int, got bool"
            )
            continue

        if not isinstance(
            value,
            expected_type,
        ):
            errors.append(
                f"{field_name}: expected "
                f"{expected_type.__name__}, "
                f"got {type(value).__name__}"
            )

    if errors:
        raise FieldTypeError(
            "; ".join(errors)
        )


# ============================================================================
# Score Normalization
# ============================================================================


def normalize_score(
    value: Any,
    *,
    minimum: float = 0.0,
    maximum: float = 100.0,
    default: Optional[float] = None,
) -> Optional[float]:
    """
    Normalize an LLM-generated score.

    Handles:
        85
        "85"
        85.5
        "85/100"
        "85%"
    """

    if value is None:
        return default

    if isinstance(
        value,
        bool,
    ):
        return default

    if isinstance(
        value,
        (int, float),
    ):
        score = float(
            value
        )

    elif isinstance(
        value,
        str,
    ):

        match = re.search(
            r"-?\d+(?:\.\d+)?",
            value,
        )

        if not match:
            return default

        score = float(
            match.group()
        )

    else:
        return default

    return max(
        minimum,
        min(
            maximum,
            score,
        ),
    )


def normalize_scores(
    data: Dict[str, Any],
    fields: Iterable[str],
) -> Dict[str, Any]:
    """
    Normalize multiple score fields.
    """

    result = dict(
        data
    )

    for field_name in fields:

        if field_name in result:

            result[
                field_name
            ] = normalize_score(
                result[field_name]
            )

    return result


# ============================================================================
# List Normalization
# ============================================================================


def normalize_list(
    value: Any,
) -> List[Any]:
    """
    Convert common LLM list formats to a Python list.

    Examples:

        ["Python", "FastAPI"]

        "Python, FastAPI"

        "Python; FastAPI"

        "Python"
    """

    if value is None:
        return []

    if isinstance(
        value,
        list,
    ):
        return value

    if isinstance(
        value,
        tuple,
    ):
        return list(
            value
        )

    if isinstance(
        value,
        str,
    ):

        value = value.strip()

        if not value:
            return []

        if "," in value:
            return [
                item.strip()
                for item in value.split(
                    ","
                )
                if item.strip()
            ]

        if ";" in value:
            return [
                item.strip()
                for item in value.split(
                    ";"
                )
                if item.strip()
            ]

        return [value]

    return [value]


def normalize_string(
    value: Any,
    default: str = "",
) -> str:
    """
    Convert an LLM field to a string.
    """

    if value is None:
        return default

    if isinstance(
        value,
        str,
    ):
        return value.strip()

    return str(
        value
    ).strip()


# ============================================================================
# Boolean Normalization
# ============================================================================


def normalize_boolean(
    value: Any,
    default: Optional[bool] = None,
) -> Optional[bool]:
    """
    Normalize common LLM boolean representations.
    """

    if isinstance(
        value,
        bool,
    ):
        return value

    if isinstance(
        value,
        (int, float),
    ):

        if value == 1:
            return True

        if value == 0:
            return False

    if isinstance(
        value,
        str,
    ):

        normalized = (
            value.strip()
            .lower()
        )

        if normalized in {
            "true",
            "yes",
            "y",
            "1",
            "correct",
            "pass",
            "passed",
        }:
            return True

        if normalized in {
            "false",
            "no",
            "n",
            "0",
            "incorrect",
            "fail",
            "failed",
        }:
            return False

    return default


# ============================================================================
# Enum Normalization
# ============================================================================


def normalize_enum(
    value: Any,
    allowed_values: Sequence[str],
    default: Optional[str] = None,
) -> Optional[str]:
    """
    Normalize a string against allowed values.
    """

    if value is None:
        return default

    normalized = str(
        value
    ).strip().lower()

    normalized_values = {
        str(item).strip().lower(): item
        for item in allowed_values
    }

    if normalized in normalized_values:
        return normalized_values[
            normalized
        ]

    return default


# ============================================================================
# Interview Response Parsing
# ============================================================================


def parse_interview_evaluation(
    text: str,
) -> Dict[str, Any]:
    """
    Parse an interview answer evaluation.
    """

    data = parse_object(
        text
    )

    data = normalize_scores(
        data,
        [
            "score",
            "correctness",
            "relevance",
            "completeness",
            "reasoning",
            "evidence",
        ],
    )

    for field_name in [
        "strengths",
        "weaknesses",
        "technical_gaps",
        "improvements",
    ]:

        if field_name in data:
            data[
                field_name
            ] = normalize_list(
                data[field_name]
            )

    for field_name in [
        "feedback",
        "explanation",
    ]:

        if field_name in data:
            data[
                field_name
            ] = normalize_string(
                data[field_name]
            )

    return data


def parse_technical_evaluation(
    text: str,
) -> Dict[str, Any]:
    """
    Parse technical interview evaluation.
    """

    data = parse_object(
        text
    )

    data = normalize_scores(
        data,
        [
            "technical_score",
            "depth_score",
            "problem_solving_score",
        ],
    )

    if "correct" in data:
        data[
            "correct"
        ] = normalize_boolean(
            data["correct"]
        )

    for field_name in [
        "strengths",
        "technical_gaps",
    ]:

        if field_name in data:
            data[
                field_name
            ] = normalize_list(
                data[field_name]
            )

    return data


def parse_communication_evaluation(
    text: str,
) -> Dict[str, Any]:
    """
    Parse communication evaluation.
    """

    data = parse_object(
        text
    )

    data = normalize_scores(
        data,
        [
            "communication_score",
            "clarity",
            "structure",
            "conciseness",
            "coherence",
            "relevance",
        ],
    )

    for field_name in [
        "strengths",
        "improvements",
    ]:

        if field_name in data:
            data[
                field_name
            ] = normalize_list(
                data[field_name]
            )

    return data


# ============================================================================
# Resume Response Parsing
# ============================================================================


def parse_resume_analysis(
    text: str,
) -> Dict[str, Any]:
    """
    Parse resume analysis output.
    """

    data = parse_object(
        text
    )

    data = normalize_scores(
        data,
        [
            "overall_score",
            "ats_score",
            "experience_match",
            "education_match",
        ],
    )

    for field_name in [
        "strengths",
        "weaknesses",
        "technical_skills",
        "relevant_experience",
        "missing_information",
        "ats_issues",
        "recommendations",
        "matched_keywords",
        "missing_keywords",
        "required_skills_matched",
        "required_skills_missing",
        "formatting_issues",
    ]:

        if field_name in data:
            data[
                field_name
            ] = normalize_list(
                data[field_name]
            )

    return data


def parse_skill_extraction(
    text: str,
) -> Dict[str, Any]:
    """
    Parse skill extraction output.
    """

    data = parse_object(
        text
    )

    skill_fields = [
        "programming_languages",
        "frameworks",
        "libraries",
        "databases",
        "cloud",
        "devops",
        "tools",
        "methodologies",
        "soft_skills",
        "domain_skills",
    ]

    for field_name in skill_fields:

        if field_name in data:
            data[
                field_name
            ] = normalize_list(
                data[field_name]
            )

    return data


# ============================================================================
# Ranking Response Parsing
# ============================================================================


def parse_ranking(
    text: str,
) -> Dict[str, Any]:
    """
    Parse candidate ranking response.
    """

    data = parse_object(
        text
    )

    rankings = data.get(
        "rankings",
        [],
    )

    if not isinstance(
        rankings,
        list,
    ):
        raise FieldTypeError(
            "'rankings' must be a list."
        )

    normalized_rankings = []

    for item in rankings:

        if not isinstance(
            item,
            dict,
        ):
            continue

        item = dict(
            item
        )

        item["score"] = normalize_score(
            item.get("score")
        )

        if "rank" in item:
            item["rank"] = normalize_score(
                item["rank"],
                minimum=1,
                maximum=100000,
            )

        for field_name in [
            "strengths",
            "gaps",
        ]:

            if field_name in item:
                item[
                    field_name
                ] = normalize_list(
                    item[field_name]
                )

        normalized_rankings.append(
            item
        )

    data[
        "rankings"
    ] = normalized_rankings

    return data


# ============================================================================
# Interview Question Parsing
# ============================================================================


def parse_interview_question(
    text: str,
) -> Dict[str, Any]:
    """
    Parse generated interview question.
    """

    data = parse_object(
        text
    )

    if "question" in data:
        data[
            "question"
        ] = normalize_string(
            data["question"]
        )

    if "difficulty" in data:
        data[
            "difficulty"
        ] = normalize_enum(
            data["difficulty"],
            [
                "easy",
                "medium",
                "hard",
                "expert",
            ],
            default="medium",
        )

    if "expected_signals" in data:
        data[
            "expected_signals"
        ] = normalize_list(
            data["expected_signals"]
        )

    return data


# ============================================================================
# Generic Validation
# ============================================================================


def validate_response(
    data: Mapping[str, Any],
    *,
    required_fields: Optional[
        Iterable[str]
    ] = None,
    field_types: Optional[
        Mapping[str, Type[Any]]
    ] = None,
) -> ValidationResult:
    """
    Validate already-parsed response data.
    """

    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(
        data,
        Mapping,
    ):
        return ValidationResult(
            valid=False,
            data={},
            errors=[
                "Response must be a mapping."
            ],
        )

    data_dict = dict(
        data
    )

    if required_fields:

        missing = find_missing_fields(
            data_dict,
            required_fields,
        )

        errors.extend(
            [
                f"Missing field: {field}"
                for field in missing
            ]
        )

    if field_types:

        for field_name, expected_type in field_types.items():

            if not has_field(
                data_dict,
                field_name,
            ):
                continue

            value = get_field(
                data_dict,
                field_name,
            )

            if value is None:
                continue

            if (
                expected_type is int
                and isinstance(
                    value,
                    bool,
                )
            ):
                errors.append(
                    f"{field_name}: expected int, got bool"
                )

            elif not isinstance(
                value,
                expected_type,
            ):
                errors.append(
                    f"{field_name}: expected "
                    f"{expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )

    return ValidationResult(
        valid=not errors,
        data=data_dict,
        errors=errors,
        warnings=warnings,
    )


# ============================================================================
# Safe Parsing
# ============================================================================


def safe_parse_json(
    text: str,
    default: Optional[
        Dict[str, Any]
    ] = None,
) -> Dict[str, Any]:
    """
    Parse JSON without raising an exception.

    Useful for non-critical AI features.
    """

    try:
        return parse_object(
            text
        )

    except ResponseParserError:
        return (
            default
            if default is not None
            else {}
        )


def safe_get_score(
    data: Mapping[str, Any],
    field_name: str,
    default: float = 0.0,
) -> float:
    """
    Safely retrieve a normalized score.
    """

    value = get_field(
        data,
        field_name,
    )

    score = normalize_score(
        value
    )

    if score is None:
        return default

    return score


# ============================================================================
# Serialization
# ============================================================================


def serialize_response(
    data: Mapping[str, Any],
    *,
    pretty: bool = False,
) -> str:
    """
    Serialize parsed response data to JSON.
    """

    try:
        return json.dumps(
            data,
            indent=2 if pretty else None,
            ensure_ascii=False,
            default=str,
        )

    except (
        TypeError,
        ValueError,
    ) as exc:

        raise ResponseParserError(
            "Unable to serialize response."
        ) from exc


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    # Exceptions
    "ResponseParserError",
    "InvalidJSONError",
    "InvalidResponseError",
    "MissingFieldError",
    "FieldTypeError",

    # Data classes
    "ParsedResponse",
    "ValidationResult",

    # Cleaning
    "clean_response",
    "remove_code_fences",
    "extract_json_object",
    "extract_json_array",

    # Parsing
    "parse_json",
    "parse_object",
    "parse_array",
    "parse_response",

    # Fields
    "find_missing_fields",
    "has_field",
    "get_field",
    "require_field",

    # Validation
    "validate_field_types",
    "validate_response",

    # Normalization
    "normalize_score",
    "normalize_scores",
    "normalize_list",
    "normalize_string",
    "normalize_boolean",
    "normalize_enum",

    # Specialized parsers
    "parse_interview_evaluation",
    "parse_technical_evaluation",
    "parse_communication_evaluation",
    "parse_resume_analysis",
    "parse_skill_extraction",
    "parse_ranking",
    "parse_interview_question",

    # Safe helpers
    "safe_parse_json",
    "safe_get_score",
    "serialize_response",
]